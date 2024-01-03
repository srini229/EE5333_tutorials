# min_vertex_cover.py
Python solution for the minimum vertex cover problem using the `mip` package as front end and `Cbc` as the ILP solver.

# min_vertex_cover.cc
C++ solution for the same minimum vertex cover problem using `Cbc` solver. `boost::python` library is used to generate Python loadable object file.
To build, use the command: `make`. This should generate `min_vertex_cover.so`. This shared object can be imported as a module in Python.

The dependencies for compiling this file are:
- Cbc solver development package
- boost::python development package
These packages are available as `coinor-libcbc-dev` and `libboost-python-dev` in the Debian/Ubuntu repositories.

You can also build this using the docker image prepared for the class [srampr/ee5333:latest](https://hub.docker.com/r/srampr/ee5333). This docker image pull/run instructions are available on the linked image's overview page.

# run_vertex_cover.py

Imports the vertex cover module (can be Python or the C++ generated .so file) and runs a sample graph whose output is `[0, 1]`.
