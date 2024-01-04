INCLUDE_DIRS=/usr/include/python3.11
LINKER_FLAGS= -lOsiCbc -lCbcSolver -lCbc -lCgl -lOsi -lOsiClp -lClp -lCoinUtils -lboost_python311 -lpython3.11
HEADERS := $(wildcard *.h)
SRCS := $(wildcard *.cpp)
OBJS := $(patsubst %.cpp,%.so,$(SRCS))

all: $(OBJS)

clean: $(OBJS)
	rm -f $(OBJS)

%.so: %.cpp $(HEADERS)
	g++ -I${INCLUDE_DIRS} -g -fPIC -shared -o $@ $< ${LINKER_FLAGS}

