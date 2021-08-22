all: test
format:
	black . -l 79
test: format
	openfisca-us test openfisca_us/tests
