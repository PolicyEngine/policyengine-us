all: build
format:
	autopep8 -r .
	black . -l 79
	linecheck . --fix
install:
	pip install -e .[dev]
	pip install --upgrade jupyter-book
test:
	pytest openfisca_us/tests/ --maxfail=0
	pytest openfisca_us/microdata/tests/
	coverage run --branch -m openfisca_us.tools.cli test openfisca_us/tests/policy/baseline
	coverage xml -i
documentation:
	jb build docs/book
build:
	python setup.py sdist bdist_wheel

changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.0.1
	build-changelog changelog.yaml --org PolicyEngine --repo openfisca-us --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml setup.py
