all: test
format:
	autopep8 -r .
	black . -l 79
test:
	openfisca-us test openfisca_us/tests
