import LEFDEFParser
d = LEFDEFParser.DEFReader()
d.readDEF('sample.def')

d.nets()[0].print()
d.nets()[0].addRect("M1", 100, 200, 300, 400)
d.nets()[0].print()
d.nets()[1].addRect("li1", 200, 400, 350, 450)

c = d.components()
if len(c):
  c[0].print()
  c[0].setLocation(8000, 10000)
  c[0].setOrient('S')
for p in d.pins():
  p.print()
  break
d.writeDEF('sample_out.def')

d = LEFDEFParser.DEFReader()
d.readDEF('c17.def')
for g in d.gcgrids():
  print(g.orient, g.x, g.num, g.step)
for l,gs in d.tracks().items():
  print(l)
  for g in gs:
    print(g.orient, g.x, g.num, g.step)
