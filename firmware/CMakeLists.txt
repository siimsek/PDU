enable_language(ASM)
option(PDU_SCOPE_PWM "Expose TA1 on an unpowered oscilloscope bench" OFF)
include(FetchContent)
FetchContent_Declare(stm32g4_device
    URL https://codeload.github.com/STMicroelectronics/cmsis_device_g4/tar.gz/25664ddc3a7624ae9627ae8c4c672073dc5b2539
    URL_HASH SHA256=29f1c6a51740012cb6fec5c75ec175b1aac1f1a98adc2989eff4f5f5dbb4c6b5
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
FetchContent_Declare(arm_cmsis
    URL https://codeload.github.com/ARM-software/CMSIS_5/tar.gz/2b7495b8535bdcb306dac29b9ded4cfb679d7e5c
    URL_HASH SHA256=9f7f0080795b1635b82d9f7b084d37011866cd78365749997391ba0f9602f9fe
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
FetchContent_MakeAvailable(stm32g4_device arm_cmsis)

set(device_templates "${stm32g4_device_SOURCE_DIR}/Source/Templates")
add_executable(pdu_g474
    stm32g474.c
    "${device_templates}/system_stm32g4xx.c"
    "${device_templates}/gcc/startup_stm32g474xx.s")
set_target_properties(pdu_g474 PROPERTIES SUFFIX ".elf" INTERPROCEDURAL_OPTIMIZATION_RELEASE ON)
set_target_properties(pdu_control PROPERTIES POSITION_INDEPENDENT_CODE OFF INTERPROCEDURAL_OPTIMIZATION_RELEASE ON)
target_compile_definitions(pdu_g474 PRIVATE STM32G474xx PDU_SCOPE_PWM=$<BOOL:${PDU_SCOPE_PWM}>)
target_include_directories(pdu_g474 SYSTEM PRIVATE
    "${stm32g4_device_SOURCE_DIR}/Include"
    "${arm_cmsis_SOURCE_DIR}/CMSIS/Core/Include")
target_link_libraries(pdu_g474 PRIVATE pdu_control m)
target_compile_options(pdu_control PRIVATE -Wall -Wextra -Werror -fno-math-errno -ffp-contract=off
    -ffunction-sections -fdata-sections)
target_compile_options(pdu_g474 PRIVATE -Wall -Wextra -Werror -ffunction-sections -fdata-sections)
target_link_options(pdu_g474 PRIVATE -nostartfiles --specs=nano.specs --specs=nosys.specs
    "-T${CMAKE_CURRENT_SOURCE_DIR}/stm32g474re.ld"
    "-Wl,--gc-sections,-Map=${CMAKE_CURRENT_BINARY_DIR}/pdu_g474.map,--print-memory-usage")
set_property(TARGET pdu_g474 APPEND PROPERTY LINK_DEPENDS "${CMAKE_CURRENT_SOURCE_DIR}/stm32g474re.ld")
add_custom_command(TARGET pdu_g474 POST_BUILD
    COMMAND "${CMAKE_OBJCOPY}" -O binary "$<TARGET_FILE:pdu_g474>" "${CMAKE_CURRENT_BINARY_DIR}/pdu_g474.bin"
    VERBATIM)
