cmake_minimum_required(VERSION 3.25)
project(pdu_control LANGUAGES C)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
find_package(Python3 3.12 REQUIRED COMPONENTS Interpreter)

set(GAINS_HEADER "${CMAKE_CURRENT_BINARY_DIR}/gains.h")
set(TIMING_HEADER "${CMAKE_CURRENT_BINARY_DIR}/pdu_timing.h")
add_custom_command(OUTPUT "${GAINS_HEADER}" "${TIMING_HEADER}"
    COMMAND "${Python3_EXECUTABLE}" "${CMAKE_CURRENT_SOURCE_DIR}/control/configure.py" "${GAINS_HEADER}" "${TIMING_HEADER}"
    DEPENDS control/configure.py control/gains.json VERBATIM)
add_library(pdu_control STATIC firmware/control.c "${GAINS_HEADER}" "${TIMING_HEADER}")
target_include_directories(pdu_control PUBLIC firmware "${CMAKE_CURRENT_BINARY_DIR}")
set_target_properties(pdu_control PROPERTIES POSITION_INDEPENDENT_CODE ON)

if(CMAKE_CROSSCOMPILING)
    add_subdirectory(firmware)
else()
    add_library(pdu_sim SHARED control/switching.c)
    target_link_libraries(pdu_sim PRIVATE pdu_control)
    if(NOT MSVC)
        target_link_libraries(pdu_sim PRIVATE m)
        target_compile_options(pdu_sim PRIVATE -Wall -Wextra -Werror -ffp-contract=off)
        target_compile_options(pdu_control PRIVATE -Wall -Wextra -Werror -ffp-contract=off)
    endif()
    set_target_properties(pdu_sim PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/$<0:>"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin/$<0:>")
endif()
