import LEFDEFParser
d = LEFDEFParser.DEFReader()
d.readDEF('c17.def')

for p in d.pins():
  print(p)
