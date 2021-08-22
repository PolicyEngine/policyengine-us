all: test
format:
	autopep8 -r .
	black . -l 79
test: format
	openfisca-us test openfisca_us/tests
