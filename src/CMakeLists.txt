INCLUDE_DIRECTORIES("../include")
LINK_DIRECTORIES(
	"../lib"
	)
SET(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g   -Wall -O2")  
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g   -Wall -O2")
#SET(CMAKE_EXE_LINKER_FLAGS "-lpthread -lrt")
SET(SEC_LIST
	plsa_train.cpp
	util.cpp
	plsa.cpp
	)
ADD_EXECUTABLE(plsa_train ${SEC_LIST})
TARGET_LINK_LIBRARIES(plsa_train tinyxml.so libglog.a pthread)
#SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_BINARY_DIR}/bin)
#TARGET_LINK_LIBRARIES(main ${PROJECT_SOURCE_DIR}/libs/libboost_regex.a)
