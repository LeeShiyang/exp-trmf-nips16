#!/usr/bin/env python

import sys, os
from os import path
from shutil import copytree, rmtree, ignore_patterns

try :
    from setuptools import setup, Extension
except :
    from distutils.core import setup, Extension

# a technique to build a shared library on windows
from distutils.command.build_ext import build_ext
build_ext.get_export_symbols = lambda x,y: []

def get_blas_link_args(blas='lapack_opt'):
    import numpy.distutils.system_info as info
    dirs = info.get_info(blas)['library_dirs']
    libs = info.get_info(blas)['libraries']
    libs_cmd = ['-l{}'.format(x) for x in libs]
    dirs_cmd = ['-L{}'.format(x) for x in dirs]
    return libs_cmd + dirs_cmd

source_codes = ["trmf/corelib/trmf.cpp"]
headers = ["trmf/corelib/rf_matrix.h", "trmf/corelib/rf_tron.h", "trmf/corelib/trmf.h"]
include_dirs = ["trmf/corelib"]
libname = "trmf.corelib.trmf"
blas_link_args = get_blas_link_args()

if sys.platform == "win32":
    dynamic_lib = Extension('liblinear.liblinear_dynamic', source_codes,
            depends=headers,
            include_dirs=["src/"],
            define_macros=[("_WIN64",""), ("_CRT_SECURE_NO_DEPRECATE","")],
            language="c++",
            extra_link_args=["-DEF:src\linear.def"])
else :
    dynamic_lib_float32 = Extension('{}_float32'.format(libname),
                                    source_codes,
                                    depends=headers,
                                    include_dirs=include_dirs,
                                    define_macros=[("ValueType","float")],
                                    extra_compile_args=["-fopenmp", "-march=native", "-O3"],
                                    extra_link_args=["-fopenmp"] + blas_link_args,
                                    language="c++")

    dynamic_lib_float64 = Extension('{}_float64'.format(libname),
                                    source_codes,
                                    depends=headers,
                                    include_dirs=include_dirs,
                                    define_macros=[("ValueType","double")],
                                    extra_compile_args=["-fopenmp", "-march=native", "-O3"],
                                    extra_link_args=["-fopenmp"] + blas_link_args,
                                    language="c++")
setup(
    name='py-trmf',
    packages=["trmf"],
    package_dir = {"liblinear":"."},
    version='1.0',
    description='Python Interface of TRMF',
    author='Hsiang-Fu Yu',
    author_email='rofu.yu@gmail.com',
    url='http://www.cs.utexas.edu/~rofuyu',
    ext_modules=[dynamic_lib_float32, dynamic_lib_float64],
    #package_data={"trmf":["corelib/*.cpp", "corelib/*.h","corelib/Makefile", "corelib/*.so"]}
    package_data={"trmf":["corelib/*.cpp", "corelib/*.h"]},
    setup_requires=["mkl", "scipy", "numpy"],
    install_requires=["mkl", "scipy", "numpy"]
)
