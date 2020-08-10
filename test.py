#!usr/bin/python3
# -*- coding: utf-8 -*-

import os

os.system('chcp 65001')
os.system('cls')

filename = "C:\\Users\\30743\\PycharmProjects\\RigActionRecorder\\main.py"
exec(compile(open(filename).read(), filename, 'exec'))
