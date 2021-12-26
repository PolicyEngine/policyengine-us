PYV=$(shell python -c "import sys;t='{v[0]}.{v[1]}'.format(v=list(sys.version_info[:2]));sys.stdout.write(t)");
all: build
format:
	autopep8 -r .
	black . -l 79
install:
	pip install -e .[dev]
test:
	pytest openfisca_us/tests/ --maxfail=0
	coverage run --branch -m openfisca_us.tools.cli test openfisca_us/tests/policy/baseline
	coverage xml
documentation:
	jb build docs/book
build:
	python setup.py sdist bdist_wheel
version:
	
