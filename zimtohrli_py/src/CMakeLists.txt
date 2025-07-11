cmake_minimum_required(VERSION 3.15)
project(zimtohrli_python)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Find audio libraries
pkg_check_modules(flac REQUIRED flac)
pkg_check_modules(ogg REQUIRED ogg)
pkg_check_modules(vorbis REQUIRED vorbis)
pkg_check_modules(vorbisenc REQUIRED vorbisenc)
pkg_check_modules(soxr REQUIRED IMPORTED_TARGET soxr)

# Include FetchContent for dependencies
include(FetchContent)

# Fetch protobuf
FetchContent_Declare(protobuf
    GIT_REPOSITORY https://github.com/protocolbuffers/protobuf.git
    GIT_TAG v26.1
    FIND_PACKAGE_ARGS NAMES protobuf
)
FetchContent_MakeAvailable(protobuf)

# Create the Python extension
add_library(_zimtohrli SHARED
    pyohrli.cc
    zimtohrli.h
    resample.h
    mos.h
)

# Set target properties for Python extension
set_target_properties(_zimtohrli PROPERTIES
    PREFIX ""
    SUFFIX ""
)

# Handle different platforms
if(WIN32)
    set_target_properties(_zimtohrli PROPERTIES SUFFIX ".pyd")
elseif(APPLE)
    set_target_properties(_zimtohrli PROPERTIES SUFFIX ".so")
else()
    set_target_properties(_zimtohrli PROPERTIES SUFFIX ".so")
endif()

# Include directories
target_include_directories(_zimtohrli PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${Python3_INCLUDE_DIRS}
)

# Link libraries
target_link_libraries(_zimtohrli
    Python3::Python
    PkgConfig::soxr
    protobuf::libprotobuf
    absl::check
    absl::span
    absl::statusor
    absl::flags_parse
)

# Compiler-specific options
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(_zimtohrli PRIVATE
        -fPIC
        -O3
        -march=native
        -freciprocal-math
        -fno-signed-zeros
        -fno-math-errno
    )
endif()

# Add preprocessor definitions
target_compile_definitions(_zimtohrli PRIVATE
    PY_SSIZE_T_CLEAN
)