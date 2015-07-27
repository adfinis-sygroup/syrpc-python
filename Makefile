SHELL := /usr/bin/env bash

.PHONY: all

install:
	@pip install --upgrade .

install-edit:
	@pip install --upgrade -e .

fasttest:
	@nosetests

nosetest: py-modules
	@nosetests --cover-package=symonitoring_rpc --with-coverage --cover-tests --cover-erase --cover-min-percentage=95

test: nosetest pep8 pylint

clean:
	git clean -f

pep8:
	pep8 --ignore=E203,E272,E221,W291,E251,E203,E501,E402,E241 symonitoring_rpc

pylint:
	pylint --disable=fixme,cyclic-import,import-error -r n symonitoring_rpc --msg-template "{path} {C}:{line:3d},{column:2d}: {msg} ({symbol})"

pylint-all:
	pylint -r n symonitoring_rpc --msg-template "{path} {C}:{line:3d},{column:2d}: {msg} ({symbol})"

py-modules:
	./.venv-test.py
	pip install --upgrade -r .test-requirements.txt
