all: build
format:
	autopep8 -r .
	black . -l 79
install:
	pip install -e .[dev]
test:
	openfisca-us test openfisca_us/tests/policy
	pytest openfisca_us/tests/ --maxfail=0
documentation:
	jb build docs/book
build:
	python setup.py sdist bdist_wheel
