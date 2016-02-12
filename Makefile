SHELL := /usr/bin/env bash

ACT := source venv/bin/activate &&

nosetest: venv
	$(ACT) nosetests --cover-package=syrpc --with-coverage --cover-tests --cover-erase --cover-min-percentage=100

test: nosetest pep8 pylint

clean:
	git clean -f

pep8:
	$(ACT) pep8 --ignore=E203,E272,E221,W291,E251,E203,E501,E402,E241 syrpc

pylint:
	$(ACT) pylint --disable=fixme,cyclic-import,import-error -r n syrpc --msg-template "{path} {C}:{line:3d},{column:2d}: {msg} ({symbol})"

pylint-all:
	$(ACT) pylint -r n syrpc --msg-template "{path} {C}:{line:3d},{column:2d}: {msg} ({symbol})"

venv:
	if [ -z "`which virtualenv`" ]; then \
		sudo pip install virtualenv; \
	fi
	virtualenv venv
	$(ACT) pip install --upgrade -r test-requirements.txt
