# -*- coding: utf-8 -*-
from __future__ import print_function

import nox

@nox.session
def checkmanifest(session):
    """ Check pythonpy-fork’s MANIFEST.in against the Git HEAD """
    session.install("-r", "requirements/nox/manifest.txt")
    session.run('python', '-m', 'check_manifest', '-v')

@nox.session
def pytest(session):
    """ Run pythonpy-fork’s entire unit-test suite """
    session.install('-r', 'requirements/nox/tests.txt')
    session.install('.')
    session.run('pytest')