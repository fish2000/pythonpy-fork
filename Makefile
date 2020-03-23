
PROJECT_NAME = pythonpy

clean: clean-build-artifacts clean-pyc

distclean: clean-cython clean-test-artifacts clean-build-artifacts

rebuild: clean-build-artifacts

dist: twine-upload

upload: clean-build-artifacts bump dist
	git push

bigupload: clean-build-artifacts bigbump dist
	git push

clean-pyc:
	find $(PROJECT_BASE) -name \*.pyc -print -delete

clean-build-artifacts:
	rm -rf build dist python_$(PROJECT_NAME).egg-info

clean-test-artifacts: clean-pyc
	rm -rf  $(PROJECT_ROOT)/.pytest_cache \
			$(PROJECT_ROOT)/.hypothesis \
			$(PROJECT_BASE)/.pytest_cache \
			$(PROJECT_BASE)/.hypothesis \
			$(PROJECT_BASE)/.nox \
			$(PROJECT_BASE)/.tox

sdist:
	python setup.py sdist

wheel:
	python setup.py bdist_wheel

twine-upload: sdist wheel
	twine upload -s $(PROJECT_BASE)/dist/*

bump:
	bumpversion --verbose patch

bigbump:
	bumpversion --verbose minor

check: clean-test-artifacts
	check-manifest -v
	python setup.py check -m -s
	travis lint .travis.yml

mypy:
	mypy --config-file mypy.ini

pytype:
	pytype --config pytype.cfg --verbosity=2

pytest:
	python -m pytest -p clu.testing.pytest

nox:
	nox --report $(PROJECT_BASE)/.noxresults.json

renox: clean-test-artifacts nox

test: check pytest

test-all: check nox

test-configuration:
	python -m pytest --setup-plan --trace-config | pygmentize -l clean -O "style=vim"

.PHONY: clean distclean rebuild
.PHONY: dist upload bigupload
.PHONY: clean-pyc
.PHONY: clean-build-artifacts clean-test-artifacts

.PHONY: sdist wheel twine-upload bump bigbump

.PHONY: check mypy pytype
.PHONY: pytest nox renox
.PHONY: test test-all test-configuration
