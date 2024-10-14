cmake_minimum_required(VERSION 3.10)
project(BackupDaemon)

set(CMAKE_CXX_STANDARD 17)

find_package(Boost 1.70 REQUIRED COMPONENTS filesystem system log log_setup)

add_executable(BackupDaemon BackupDaemon.cpp)
target_link_libraries(BackupDaemon Boost::filesystem Boost::system Boost::log Boost::log_setup)
