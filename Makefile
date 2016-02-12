PROJECT := syrpc
SHELL := /usr/bin/env bash

ACT := source venv/bin/activate &&

pytest: venv
	$(ACT) py.test --timeout=300 --doctest-modules --cov-report term-missing --cov=$(PROJECT) --cov-fail-under=100 --no-cov-on-fail $(PROJECT)

test: pytest flake8

clean:
	git clean -f

flake8:
	$(ACT) flake8 --doctests -j auto --ignore=E221,E222,E251,E272,E241,E203 $(PROJECT)

venv:
	if [ -z "`which virtualenv`" ]; then \
		sudo pip install virtualenv; \
	fi
	virtualenv venv
	$(ACT) pip install --upgrade -r test-requirements.txt
