#!/usr/bin/env python
# Copyright (c) 2021-2022 Istituto Nazionale di Fisica Nucleare
# SPDX-License-Identifier: MIT


import tensorflow as tf
import numpy as np
# import cupy as cp
import sys
import time

# READ ARGS FROM COMMAND LINE
# Raise error if correct arguments aren't given
if len(sys.argv) != 4:
    print("Matmul benchmark need 3 arguments:")
    print("- device")
    print("- matrices first dimension")
    print("- matrices second dimension")
    sys.exit(1)

dev = sys.argv[1]
shape_1 = int(sys.argv[2])
shape_2 = int(sys.argv[3])


# dev = 'gpu'
# shape_1 = 20
# shape_2 = 30

# SET DEVICE

if dev == 'cpu':
    d = '/cpu:0'
elif dev == 'gpu':
    if tf.config.list_physical_devices('GPU') == 0:
        print("GPU unavailable :(")
        sys.exit(0)
    d = '/device:GPU:0'

with tf.device(d):

    # TENSORFLOW
    tf.random.set_seed(5)
    matrix_1_tf = tf.random.normal([shape_1, shape_2])
    matrix_2_tf = tf.random.normal([shape_2, shape_1])

    # NUMPY
    matrix_1_np = np.random.randn(shape_1, shape_2)
    matrix_2_np = np.random.randn(shape_2, shape_1)

    # CUPY
    # matrix_1_cp = cp.random.normal(size=shape_1)
    # matrix_2_cp = cp.random.normal(size=shape_2)

    start_time_tf = time.time()
    tf.linalg.matmul(matrix_1_tf, matrix_2_tf)
    multiplication_time_tf = time.time() - start_time_tf

    start_time_np = time.time()
    np.matmul(matrix_1_np, matrix_2_np)
    multiplication_time_np = time.time() - start_time_np

    # start_time_cp = time.time()
    # cp.matmul(matrix_1_cp, matrix_2_cp)
    # multiplication_time_cp = time.time() - start_time_cp

print("Matrix multiplcation time with numpy: %s s" % multiplication_time_np)
# print("Matrix multiplcation time with cupy: {} s" .format(multiplication_time_cp))
print("Matrix multiplcation time: %s s" % multiplication_time_tf)
