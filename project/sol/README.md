# EE5333 Introduction to Physical Design Automation - End sem project

# Generate solution file

Create a sample def file containing solutions for three nets of `c17`.
```
python3 writeSol.py
```
This should create a `c17_out.def` in the same directory.

# Running the checker

The script `checker.py` does (a) spacing DRC check and (b) connectivity check for all nets.
It requires the package `rtree`, which can be installed using `pip install rtree`.
```
python3 checker.py -i ../def/c17.def -o ./c17_out.def -l ../lef/sky130.lef
```
Total number of open (disconnected) nets and the number of spacing violations are reported on console.


There is an optional visualizer for the placement, which can be invoked using the `-p` argument.
```
python3 checker.py -i ../def/c17.def -o ./c17_out.def -l ../lef/sky130.lef -p
```

