#!/usr/bin/env python
from setuptools import setup
import sys

py_entry = 'ppy%s = pythonpy.__main__:main'
pycompleter_entry = 'ppycompleter%s = pythonpy.pycompleter:main'
endings = ('', sys.version[:1], sys.version[:3])
entry_points_scripts = []

for e in endings:
    entry_points_scripts.append(py_entry % e)
    entry_points_scripts.append(pycompleter_entry % e)

setup(
    name='pythonpy-fork',
    version='0.5.0',
    description='python -c, with tab completion and shorthand; fish2k fork',
    license='MIT',
    url='https://github.com/fish2000/pythonpy-fork',
    long_description='https://github.com/fish2000/pythonpy-fork',
    packages=['pythonpy', 'pythonpy.completion'],
    package_data={'pythonpy': ['completion/pycompletion.sh']},
    scripts=['pythonpy/find_pycompletion.sh'],
    entry_points = {
        'console_scripts': entry_points_scripts
    },
)
