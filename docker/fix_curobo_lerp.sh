#!/bin/bash
# Fix for curobo curobolib JIT compilation on CUDA 13 / torch cu130 (Jetson Thor, sm_110).
#
# Background:
#   The prebuilt kinematics_fused_cu.so shipped in the base image was built against an
#   older torch whose c10::cuda::c10_cuda_check_implementation() took `int` for the line
#   arg (symbol ...S2_ib). torch 2.13+cu130 exports the `unsigned int` variant (...S2_jb),
#   so the prebuilt binary fails to load with an undefined-symbol error. curobo then falls
#   back to JIT-compiling the extension, which fails because helper_math.h defines a global
#     float lerp(float, float, float)
#   that conflicts with C++20 std::lerp (nvcc compiles with -std=c++20 under torch cu130).
#
# Fix:
#   Guard the scalar float lerp overload behind __cpp_lib_interpolate (defined when the
#   standard library provides std::lerp). The scalar overload is unused inside curobo's
#   kernels, and the float2/float3/float4 overloads do not collide with std::lerp, so this
#   removes the redeclaration conflict without changing behaviour. helper_math.h is shared
#   by all curobolib extensions, so patching it once fixes every JIT build.
#
# torch cu130 is required (it is the only build whose arch list includes sm_110 / Thor),
# so recompiling curobo against it is the only option; the prebuilt binary cannot be reused.

set -e

HELPER="/opt/ros/jazzy/lib/python3.12/site-packages/curobo/curobolib/cpp/helper_math.h"

if [ ! -f "$HELPER" ]; then
    echo "Warning: helper_math.h not found at $HELPER"
    exit 0
fi

echo "Applying curobo helper_math.h lerp fix..."

cp -n "$HELPER" "${HELPER}.original" || true

python3 - "$HELPER" << 'PYTHON_SCRIPT'
import sys

file_path = sys.argv[1]

with open(file_path, 'r') as f:
    content = f.read()

if "__cpp_lib_interpolate" in content:
    print("File already patched, skipping...")
    sys.exit(0)

old = (
    "inline __device__ __host__ float lerp(float a, float b, float t)\n"
    "{\n"
    "    return a + t*(b-a);\n"
    "}"
)
new = (
    "#if !defined(__cpp_lib_interpolate)   // avoid clash with C++20 std::lerp\n"
    "inline __device__ __host__ float lerp(float a, float b, float t)\n"
    "{\n"
    "    return a + t*(b-a);\n"
    "}\n"
    "#endif"
)

if old not in content:
    print("ERROR: scalar lerp definition not found; helper_math.h may have changed.")
    sys.exit(1)

content = content.replace(old, new, 1)

with open(file_path, 'w') as f:
    f.write(content)

print("Patch applied successfully!")
PYTHON_SCRIPT

echo "curobo helper_math.h lerp fix applied."
