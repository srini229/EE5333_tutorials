import LEFDEFParser
d = LEFDEFParser.DEFReader()
d.readDEF('../def/c17.def')
for n in d.nets():
  if n.name() == "N1":
    n.addRect("met1", 15410, 25940, 16790, 26080)
  elif n.name() == "N1_d":
    n.addRect("met1", 5220, 28320, 7130, 28460)
    n.addRect("met2", 5220, 28320, 5360, 37740)
  elif n.name() == "N2":
    n.addRect("met2", 18100, 23900, 18240, 26080)
    n.addRect("met1", 18100, 25940, 18700, 26080)
    n.addRect("met1", 18100, 23220, 19160, 23360)
    n.addRect("met2", 18100, 23220, 18240, 24040)
d.writeDEF('c17_out.def')
