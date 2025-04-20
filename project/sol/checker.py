#!/usr/bin/env python3
import LEFDEFParser
from LEFDEFParser import Rect

skipCells = {"sky130_fd_sc_hd__decap_3", "sky130_fd_sc_hd__decap_4", "sky130_fd_sc_hd__decap_6", "sky130_fd_sc_hd__decap_8",\
            "sky130_fd_sc_hd__decap_12", "sky130_fd_sc_hd__fill_1", "sky130_fd_sc_hd__fill_2", "sky130_fd_sc_hd__fill_4",
            "sky130_fd_sc_hd__fill_8", "sky130_fd_sc_hd__lpflow_decapkapwr_3", "sky130_fd_sc_hd__lpflow_decapkapwr_4",\
            "sky130_fd_sc_hd__lpflow_decapkapwr_6", "sky130_fd_sc_hd__lpflow_decapkapwr_8", "sky130_fd_sc_hd__lpflow_decapkapwr_12", \
            "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_1", "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_2", \
            "sky130_fd_sc_hd__lpflow_lsbuf_lh_hl_isowell_tap_4", "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_1", \
            "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_2", "sky130_fd_sc_hd__lpflow_lsbuf_lh_isowell_tap_4", "sky130_fd_sc_hd__tap_1", \
            "sky130_fd_sc_hd__tap_2", "sky130_fd_sc_hd__tapvgnd2_1", "sky130_fd_sc_hd__tapvgnd_1", \
            "sky130_fd_sc_hd__tapvpwrvgnd_1", "sky130_ef_sc_hd__decap_12"}

layerColors = { 'li1': 'red', 'met1': 'blue', 'met2': 'green', 'met3': 'orange', 'met4': 'magenta', 'met5': 'cyan' }

skipNets = {'clk', 'VPWR', 'VGND'}

adjLayer = {
  'li1':  ['met1'],
  'met1': ['li1',  'met2'],
  'met2': ['met1', 'met3'],
  'met3': ['met2', 'met4'],
  'met4': ['met3', 'met5'],
  'met5': ['met4']
}

layerWidth = dict()
layerSpacing = dict()

class Inst:
  def __init__(self, comp, macro):
    self._comp = comp
    self._macro = macro
    origin = comp.location()
    self._bbox = Rect(origin.x, origin.y, origin.x + macro.xdim(), origin.y + macro.ydim())
    self._pins = dict()
    self._obsts = dict()
    for p in macro.pins():
      shapes = dict()
      for port in p.ports():
        for layer, rects in port.items():
          if layer not in layerColors: continue
          if layer not in shapes: shapes[layer] = list()
          for v in rects:
            r = Rect(v.ll.x, v.ll.y, v.ur.x, v.ur.y)
            r.transform(comp.orient(), origin, macro.xdim(), macro.ydim())
            shapes[layer].append(r)
      self._pins[p.name()] = shapes

    for layer, rects in macro.obstructions().items():
      if layer not in layerColors: continue
      if layer not in self._obsts: self._obsts[layer] = list()
      for v in rects:
        r = Rect(v.ll.x, v.ll.y, v.ur.x, v.ur.y)
        r.transform(comp.orient(), origin, macro.xdim(), macro.ydim())
        self._obsts[layer].append(r)


class Net:
  def __init__(self, net, insts, pins, idx):
    self._name = net.name()
    self._pins = dict()
    self._id   = idx
    self._sol  = net.rects()
    for p in net.pins():
      if p[0] in insts:
        self._pins[p] = insts[p[0]]._pins[p[1]]
      elif p[0] == 'PIN' and p[1] in pins:
        self._pins[p] = pins[p[1]]


def plotInsts(insts, pins):
  from matplotlib.patches import Rectangle
  from matplotlib.collections import PatchCollection
  import matplotlib.pyplot as plt
  xmin, ymin = 1e30, 1e30
  xmax, ymax = 0, 0
  for inst in insts.values():
    xmin, ymin = min(xmin, inst._bbox.ll.x), min(ymin, inst._bbox.ll.y)
    xmax, ymax = max(xmax, inst._bbox.ur.x), max(ymax, inst._bbox.ur.y)

  for p, lr in pins.items():
    for layer, rects in lr.items():
      for r in rects:
        xmin, ymin = min(xmin, r.ll.x), min(ymin, r.ll.y)
        xmax, ymax = max(xmax, r.ur.x), max(ymax, r.ur.y)
  
  fig = plt.figure()
  plt.xlim(xmin, xmax)
  plt.ylim(ymin, ymax)

  patches = dict()
  pinLabels = []
  obsts = dict()

  def add_patches(pats, lr):
      for layer, rects in lr.items():
        if layer not in pats: pats[layer] = list()
        for r in rects:
          patch = Rectangle((r.ll.x, r.ll.y), r.width(), r.height(), alpha=0.4, ec=layerColors[layer], facecolor=layerColors[layer])
          pats[layer].append(patch)

  for inst in insts.values():
    ca = plt.gca()
    ca.add_patch(Rectangle((inst._bbox.ll.x, inst._bbox.ll.y), inst._bbox.width(), inst._bbox.height(), alpha=0.25, ec="black", facecolor="grey"))
    ca.text(inst._bbox.xcenter(), inst._bbox.ycenter(), inst._comp.name())
    for p, lr in inst._pins.items():
      add_patches(patches, lr)
      for layer, rects in lr.items():
        if len(rects):
          r = rects[0]
          pinLabels.append(ca.text(r.xcenter(), r.ycenter(), p))
          break

    add_patches(obsts, inst._obsts)

  for p, lr in pins.items():
    add_patches(patches, lr)
    for layer, rects in lr.items():
      if len(rects):
        r = rects[0]
        pinLabels.append(ca.text(r.xcenter(), r.ycenter(), p))
        break


  patchByLayer = {k:PatchCollection(v, match_original=True, alpha=0.4) for k, v in patches.items()}
  from matplotlib.widgets import CheckButtons
  colors = [layerColors[layer] for layer in patchByLayer.keys()]
  patchByLayer['pin labels'] = pinLabels
  colors.append('black')
  for layer, pat in obsts.items():
    patchByLayer[f'obst({layer})'] = PatchCollection(pat, match_original=True, alpha=0.4)
    colors.append(layerColors[layer])

  for k, v in patchByLayer.items():
    if k != 'pin labels': ca.add_collection(v)
  
  rax = plt.axes([0.9, 0.4, 0.1, 0.15])
  check = CheckButtons(ax=rax, labels=patchByLayer.keys(), label_props={'color': colors},
      actives=[True for layer in patchByLayer.keys()],
      frame_props={'edgecolor': colors}, check_props={'facecolor': colors})

  def update(label):
    ln = patchByLayer[label]
    if label != 'pin labels':
      ln.set_visible(not ln.get_visible())
      ln.figure.canvas.draw_idle()
    else:
      for txt in ln:
        txt.set_visible(not txt.get_visible())
      txt.figure.canvas.draw_idle()

  check.on_clicked(update)

  plt.show()

  
#for inst in insts:
#  print(inst._comp.name(), inst._comp.location(), inst._macro.name())

def buildTree(nets, insts):
  import rtree
  lT = {layer: rtree.index.Index() for layer in layerColors}
  obstid = len(nets)

  count = 0
  for inst in insts.values():
    for layer, rects in inst._obsts.items():
      for r in rects:
        lT[layer].insert(count, (r.ll.x, r.ll.y, r.ur.x, r.ur.y), obj=obstid)
        count += 1

  for net in nets:
    for layer, rects in net._sol.items():
      for r in rects:
        lT[layer].insert(count, (r.ll.x, r.ll.y, r.ur.x, r.ur.y), obj=net._id)
        count += 1

    for p, lr in net._pins.items():
      for layer, rects in lr.items():
        for r in rects:
          lT[layer].insert(count, (r.ll.x, r.ll.y, r.ur.x, r.ur.y), obj=net._id)
          count += 1

  return lT

def checkSpacing(layerTrees, nets, insts):
# check spacing DRC violations by querying for rectangles that overlap the shape bounding box bloated by spacing
  numViolations = 0
  for net in nets:
    for layer, rects in net._sol.items():
      s = layerSpacing[layer]
      for r in rects:
        nbrs = list(layerTrees[layer].intersection((r.ll.x - s, r.ll.y - s, r.ur.x + s, r.ur.y + s), objects=True))
        for nbr in nbrs:
          if net._id != nbr.object:
            numViolations += 1
            if nbr.object < len(nets):
              print(f"[{{'net1' : '{net._name}', 'shape' : ({layer}, [{r.ll.x}, {r.ll.y}, {r.ur.x}, {r.ur.y}])}}, {{'net2' : '{nets[nbr.object]._name}', 'shape' : {[int(i) for i in nbr.bbox]}}}]")
            elif nbr.object == len(nets):
              numViolations += 1
              print(f"[{{'net1' : '{net._name}', 'shape' : ({layer}, [{r.ll.x}, {r.ll.y}, {r.ur.x}, {r.ur.y}])}}, {{'net2' : 'obst', 'shape' : {[int(i) for i in nbr.bbox]}}}]")
            else:
              assert(0)

  numViolations //= 2

  return numViolations


def addNeighbours(G, r, layer, nid, layerTrees):
# find count of current rect
  nbrs = list(layerTrees[layer].intersection((r.ll.x - 1, r.ll.y - 1, r.ur.x + 1, r.ur.y + 1), objects=True))
  for nbr in nbrs:
    if nid == nbr.object and nbr.bbox[0] == r.ll.x and nbr.bbox[1] == r.ll.y and nbr.bbox[2] == r.ur.x and nbr.bbox[3] == r.ur.y:
      curr = nbr.id
      break
  G.add_node(curr)
            
# add current layer neighbours
  for nbr in nbrs:
    if nid == nbr.object and curr != nbr.id:
      G.add_node(nbr.id)
      G.add_edge(curr, nbr.id)

# add adjacent layer neighbours
  for aly in adjLayer[layer]:
    nbrs = list(layerTrees[aly].intersection((r.ll.x, r.ll.y, r.ur.x, r.ur.y), objects=True))
    for nbr in nbrs:
      if nid == nbr.object:
        G.add_node(nbr.id)
        G.add_edge(curr, nbr.id)

def checkConnectivity(layerTrees, nets, insts):
  import networkx as nx
  numOpens = 0
  for net in nets:
    G = nx.Graph()
    for layer, rects in net._sol.items():
      for r in rects:
        addNeighbours(G, r, layer, net._id, layerTrees)

    for p, shapes in net._pins.items():
      for layer, rects in shapes.items():
        for r in rects:
          addNeighbours(G, r, layer, net._id, layerTrees)

    if len(G.nodes()):
      if not nx.is_connected(G):
        numOpens += 1

  return numOpens

def check(nets, insts):
  layerTrees = buildTree(nets, insts)
  nViols = checkSpacing(layerTrees, nets, insts)
  print(f"Total number of spacing violations : {nViols}")

  nOpens = checkConnectivity(layerTrees, nets, insts)
  print(f"Total number of nets : {len(nets)}")
  print(f"Total number of open nets : {nOpens}")

if __name__ == '__main__':
  import argparse

  ap = argparse.ArgumentParser()
  ap.add_argument("-l", "--leff", type=str, default="", help='<lef file>')
  ap.add_argument("-o", "--odeff", type=str, default="", help='<output def file>')
  ap.add_argument("-i", "--ideff", type=str, default="", help='<input def file>')
  ap.add_argument("-p", "--plot", action='store_true')
  args = ap.parse_args()
  leff = LEFDEFParser.LEFReader()
  ideff = LEFDEFParser.DEFReader()
  odeff = LEFDEFParser.DEFReader()
  if args.leff != "" and args.ideff != "" and args.odeff != "":
    leff.readLEF(args.leff)
    lefDict = {m.name() : m for m in leff.macros()}
    ideff.readDEF(args.ideff)
    odeff.readDEF(args.odeff)

    for layer in leff.layers():
      layerWidth[layer.name()] = layer.width()
      layerSpacing[layer.name()] = layer.pitch() - layer.width()

    insts = {inst.name():Inst(inst, lefDict[inst.macro()]) for inst in ideff.components() if inst.macro() not in skipCells}
    
    pins = dict()
    for p in ideff.pins():
      pn = p.name()
      pins[pn] = dict()
      for port in p.ports():
        for layer, rects in port.items():
          if layer not in pins[pn]: pins[pn][layer] = list()
          for r in rects:
            pins[pn][layer].append(Rect(r.ll.x, r.ll.y, r.ur.x, r.ur.y))

    nets = list()
    idx = 0
    for net in ideff.nets():
      if net.name() not in skipNets:
        nets.append(Net(net, insts, pins, idx))
        idx += 1

    netDict = dict()
    for net in nets:
      netDict[net._name] = net
    for net in odeff.nets():
      if net.name() in netDict:
        netDict[net.name()]._sol = net.rects()

    if (args.plot): plotInsts(insts, pins)
    check(nets, insts)
    
