#!/usr/bin/env python
from setuptools import setup
import sys, os

PROJECT_NAME = 'pythonpy'

# PROJECT DIRECTORY
CWD = os.path.dirname(__file__)
BASE_PATH = os.path.join(
            os.path.abspath(CWD), PROJECT_NAME)

py_entry = 'py%s = pythonpy.__main__:main'
pycompleter_entry = 'pycompleter%s = pythonpy.pycompleter:main'
endings = ('', sys.version[:1], sys.version[:3])
entry_points_scripts = []

# PROJECT VERSION & METADATA
__version__ = "<undefined>"
try:
    exec(compile(
        open(os.path.join(BASE_PATH,
            '__version__.py')).read(),
            '__version__.py', 'exec'))
except:
    __version__ = '0.5.3'

for e in endings:
    entry_points_scripts.append(py_entry % e)
    entry_points_scripts.append(pycompleter_entry % e)

setup(
    name='pythonpy-fork',
    version=__version__,
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
