INCLUDE_DIRS=/usr/include/python3.11
LINKER_FLAGS= -lOsiCbc -lCbcSolver -lCbc -lCgl -lOsi -lOsiClp -lClp -lCoinUtils -lboost_python311 -lpython3.11

min_vertex_cover.so: min_vertex_cover.cpp
	g++ -I${INCLUDE_DIRS} -O3 -fPIC -shared -o min_vertex_cover.so min_vertex_cover.cpp ${LINKER_FLAGS}
