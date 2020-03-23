#!/usr/bin/env python3
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from pythonpy.pyeval import pyeval
import sys

def main():
    out = pyeval(argv=sys.argv[1:])
    print(out, end='')