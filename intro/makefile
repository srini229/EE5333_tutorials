INCLUDE_DIRS=/usr/include/python3.11
LINKER_FLAGS= -lOsiCbc -lCbcSolver -lCbc -lCgl -lOsi -lOsiClp -lClp -lCoinUtils -lboost_python311 -lpython3.11
SRCS := $(wildcard *.cpp)
OBJS := $(patsubst %.cpp,%.so,$(SRCS))

%.so: %.cpp 
	g++ -I${INCLUDE_DIRS} -O3 -fPIC -shared -o $@ $< ${LINKER_FLAGS}

main: $(OBJS)
	echo
