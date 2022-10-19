all: build
format:
	black . -l 79
	linecheck . --fix
install:
	pip install -e .[dev]
	pip install --upgrade jupyter-book
test:
	coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
	coverage xml -i
	pytest policyengine_us/tests/ --maxfail=0
documentation:
	jb clean docs
	jb build docs
	python policyengine_us/tools/add_plotly_to_book.py docs/build
build:
	rm policyengine_us/data/storage/*.h5 | true
	python setup.py sdist bdist_wheel
changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.0.1 --append-file changelog_entry.yaml
	build-changelog changelog.yaml --org PolicyEngine --repo policyengine-us --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml setup.py
	rm changelog_entry.yaml || true
	touch changelog_entry.yaml
