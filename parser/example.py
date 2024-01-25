import LEFDEFParser as LDP
d = LDP.DEFReader()
d.readDEF('example.def')
l = LDP.LEFReader()
l.readLEF('Nangate.lef')

print([(c.name(), c.macro()) for c in d.components()])
print([n.name() for n in d.nets()])
for n in d.nets():
    print(n.name(), [p for p in n.pins()])
print([p.name() for p in d.pins()])


