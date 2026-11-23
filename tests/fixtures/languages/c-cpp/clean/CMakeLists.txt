cmake_minimum_required(VERSION 3.20)
project(greeting LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_library(greeting src/greeting.cpp)
target_include_directories(greeting PUBLIC src)

enable_testing()
add_executable(greeting_check tests/greeting_check.cpp)
target_link_libraries(greeting_check PRIVATE greeting)
add_test(NAME greeting_check COMMAND greeting_check)
