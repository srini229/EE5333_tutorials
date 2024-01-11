import LEFDEFParser
l = LEFDEFParser.LEFReader()
l.readLEF('Nangate.lef')
#for m in l.macros():
#    m.print()

r = LEFDEFParser.Rect(0, 0, 10, 10)
print(r.str())

m = l.macros()[0]
print(m.name(), [p.name() for p in m.pins()], m.xdim(), m.ydim())

for p in m.pins():
    print(p.name(), p.direction(), p.use())
    for port in p.ports():
        for l,v in port.items():
            print(l, [i.str() for i in v])

for l, v in m.obstructions().items():
    print(l, [i.str() for i in v])
m.print()
