format:
	black . -l 79
test: format
	openfisca test -c openfisca_us openfisca_us/tests/baseline
