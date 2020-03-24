#!/usr/bin/env python3
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from pythonpy.pyeval import pyeval
import pydoc

def main():
    out, pager = pyeval()
    if pager:
        pydoc.pager(out)
    else:
        print(out, end='')
