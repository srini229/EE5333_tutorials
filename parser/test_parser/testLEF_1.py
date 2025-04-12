import LEFDEFParser
l = LEFDEFParser.LEFReader()
l.readLEF('sky130.lef')
layerMap = {l.name():l for l in l.layers()}
for k,v in layerMap.items():
    print(k, v.name(), v.width(), v.spacing(), v.pitch(), v.offset())
    for i, w in enumerate(v.spacingTable().width):
        for j, p in enumerate(v.spacingTable().prl):
            print(p, w, v.spacingTable().spacing[i][j])
    for p, w in zip(v.spacingTable().prl, v.spacingTable().width):
        print(p, w)
    print(v.spacingTable().spacing)

r = LEFDEFParser.Rect(0, 0, 10, 10)
print(r)

m = l.macros()[0]
print(m.name(), [p.name() for p in m.pins()], m.xdim(), m.ydim())

for p in m.pins():
    print(p)
#    print(p.name(), p.direction(), p.use())
#    for port in p.ports():
#        for layer, v in port.items():
#            print(layer, [i.str() for i in v])

for layer, v in m.obstructions().items():
    print(layer, [i for i in v])
print(m)

macro_dict = dict()
for m in l.macros():
    macro_dict[m.name()] = m
#print(macro_dict)
