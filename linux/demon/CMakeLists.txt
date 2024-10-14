cmake_minimum_required(VERSION 3.10)
project(BackupDaemon)

set(CMAKE_CXX_STANDARD 17)

# Укажите путь к Boost
set(BOOST_ROOT "C:/msys64/mingw64/boost/boost_1_86_0")
set(BOOST_INCLUDEDIR "C:/msys64/mingw64/boost/boost_1_86_0")
set(BOOST_LIBRARYDIR "C:/msys64/mingw64/boost/boost_1_86_0/lib")

find_package(Boost 1.70 REQUIRED COMPONENTS filesystem system log log_setup)

add_executable(BackupDaemon BackupDaemon.cpp)
target_link_libraries(BackupDaemon Boost::filesystem Boost::system Boost::log Boost::log_setup)
