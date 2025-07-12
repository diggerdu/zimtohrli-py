cmake_minimum_required(VERSION 3.15)
project(zimtohrli_python_clean)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

message(STATUS "Building Zimtohrli Python binding (ViSQOL-free, no protobuf)")
message(STATUS "CMAKE_CURRENT_SOURCE_DIR: ${CMAKE_CURRENT_SOURCE_DIR}")
message(STATUS "CMAKE_CURRENT_BINARY_DIR: ${CMAKE_CURRENT_BINARY_DIR}")

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Find minimal audio libraries (only what core Zimtohrli needs)
message(STATUS "Checking for minimal audio libraries...")
pkg_check_modules(FLAC REQUIRED flac)
pkg_check_modules(SOXR REQUIRED soxr)

# Optional: Check for additional audio libraries but don't require them
pkg_check_modules(OGG ogg)
pkg_check_modules(VORBIS vorbis)
pkg_check_modules(VORBISENC vorbisenc)

if(OGG_FOUND)
    message(STATUS "✅ OGG found (optional): ${OGG_VERSION}")
else()
    message(STATUS "⚠️  OGG not found (optional)")
endif()

if(VORBIS_FOUND)
    message(STATUS "✅ Vorbis found (optional): ${VORBIS_VERSION}")
else()
    message(STATUS "⚠️  Vorbis not found (optional)")
endif()

message(STATUS "✅ All required audio libraries found (flac + soxr)")

# Create minimal absl replacements (no system check needed)
message(STATUS "Creating minimal absl replacements...")

# Create minimal absl replacements
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/absl/log")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/absl/types")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/absl/base")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/absl/flags")
file(MAKE_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/absl/status")

# Minimal check.h replacement
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/absl/log/check.h" 
"#pragma once
#include <cassert>
#include <iostream>

#define CHECK(condition) assert(condition)
#define CHECK_EQ(a, b) assert((a) == (b))
#define CHECK_NE(a, b) assert((a) != (b))
#define CHECK_LT(a, b) assert((a) < (b))
#define CHECK_LE(a, b) assert((a) <= (b))
#define CHECK_GT(a, b) assert((a) > (b))
#define CHECK_GE(a, b) assert((a) >= (b))
#define CHECK_NOTNULL(ptr) assert((ptr) != nullptr); (ptr)

#define DCHECK CHECK
#define DCHECK_EQ CHECK_EQ
#define DCHECK_NE CHECK_NE
#define DCHECK_LT CHECK_LT
#define DCHECK_LE CHECK_LE
#define DCHECK_GT CHECK_GT
#define DCHECK_GE CHECK_GE
")

# Minimal span.h replacement
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/absl/types/span.h"
"#pragma once
#include <vector>
#include <array>

namespace absl {
template<typename T>
class Span {
private:
    T* data_;
    size_t size_;
public:
    Span() : data_(nullptr), size_(0) {}
    Span(T* data, size_t size) : data_(data), size_(size) {}
    Span(std::vector<T>& vec) : data_(vec.data()), size_(vec.size()) {}
    template<size_t N>
    Span(std::array<T, N>& arr) : data_(arr.data()), size_(N) {}
    
    T* data() const { return data_; }
    size_t size() const { return size_; }
    bool empty() const { return size_ == 0; }
    T& operator[](size_t i) const { return data_[i]; }
    T* begin() const { return data_; }
    T* end() const { return data_ + size_; }
};
}
")

# Minimal statusor.h replacement  
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/absl/status/statusor.h"
"#pragma once
#include <optional>
#include <stdexcept>

namespace absl {
template<typename T>
class StatusOr {
private:
    std::optional<T> value_;
    bool ok_;
public:
    StatusOr(const T& value) : value_(value), ok_(true) {}
    StatusOr() : ok_(false) {}
    
    bool ok() const { return ok_; }
    const T& value() const { 
        if (!ok_) throw std::runtime_error(\"StatusOr not ok\");
        return *value_; 
    }
    T& value() { 
        if (!ok_) throw std::runtime_error(\"StatusOr not ok\");
        return *value_; 
    }
    const T& operator*() const { return value(); }
    T& operator*() { return value(); }
};
}
")

# Minimal flags_parse.h replacement
file(WRITE "${CMAKE_CURRENT_BINARY_DIR}/absl/flags/parse.h"
"#pragma once
#include <vector>
#include <string>

namespace absl {
inline std::vector<char*> ParseCommandLine(int argc, char* argv[]) {
    return std::vector<char*>(argv, argv + argc);
}
}
")

# Create the Python extension
message(STATUS "Creating Python extension...")

add_library(_zimtohrli SHARED
    pyohrli.cc
)

# Set target properties for Python extension
set_target_properties(_zimtohrli PROPERTIES
    PREFIX ""
)

# Get Python extension suffix
execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))"
    OUTPUT_VARIABLE PYTHON_EXT_SUFFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

if(PYTHON_EXT_SUFFIX)
    set_target_properties(_zimtohrli PROPERTIES SUFFIX ${PYTHON_EXT_SUFFIX})
    message(STATUS "Using Python extension suffix: ${PYTHON_EXT_SUFFIX}")
else()
    # Fallback to platform-specific suffixes
    if(WIN32)
        set_target_properties(_zimtohrli PROPERTIES SUFFIX ".pyd")
    else()
        set_target_properties(_zimtohrli PROPERTIES SUFFIX ".so")
    endif()
    message(STATUS "Using fallback extension suffix")
endif()

# Include directories
target_include_directories(_zimtohrli PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${Python3_INCLUDE_DIRS}
    ${CMAKE_CURRENT_BINARY_DIR}  # For minimal absl replacements
    ${SOXR_INCLUDE_DIRS}  # For soxr.h
)

# Link libraries
message(STATUS "Linking libraries...")

target_link_libraries(_zimtohrli PRIVATE
    Python3::Python
    ${SOXR_LIBRARIES}
)

# Add library directories
target_link_directories(_zimtohrli PRIVATE
    ${SOXR_LIBRARY_DIRS}
)

# Add compile definitions
target_compile_definitions(_zimtohrli PRIVATE
    PY_SSIZE_T_CLEAN
)

# Compiler-specific options
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" OR CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
    target_compile_options(_zimtohrli PRIVATE
        -fPIC
        -O2
    )
endif()

message(STATUS "✅ Clean Zimtohrli build configuration completed!")
message(STATUS "📦 This build includes only core Zimtohrli functionality")
message(STATUS "🚫 No ViSQOL, no protobuf, minimal dependencies")