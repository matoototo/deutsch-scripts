cmake_minimum_required(VERSION 2.8.12)
project(order_articles)

add_definitions("-std=c++17")

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable(order_articles order_articles.cpp)
target_link_libraries(order_articles ${CONAN_LIBS})
