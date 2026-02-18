all: build
format:
	uv run black . -l 79
	linecheck . --fix
install:
	pip install -e .[dev]
test:
	pytest policyengine_us/tests/ --maxfail=0
	coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
	coverage xml -i
test-yaml-structural:
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/contrib --exclude states
test-yaml-structural-heavy:
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/contrib/states --batches 1
test-yaml-no-structural-states:
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/gov/states --batches 2 --exclude ny
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/gov/states/ny --batches 1
test-yaml-no-structural-other:
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline --batches 1 --exclude states
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/household --batches 1
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/contrib --batches 1
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/reform --batches 1
test-other:
	pytest policyengine_us/tests/ --maxfail=0
coverage:
	coverage combine
	coverage xml -i
documentation:
	jb clean docs
	jb build docs
	python policyengine_us/tools/add_plotly_to_book.py docs/_build
build:
	rm policyengine_us/data/storage/*.h5 | true
	python -m build
changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.0.1 --append-file changelog_entry.yaml
	build-changelog changelog.yaml --org PolicyEngine --repo policyengine-us --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml pyproject.toml
	rm changelog_entry.yaml || true
	touch changelog_entry.yaml
dashboard:
	python policyengine_us/data/datasets/cps/enhanced_cps/update_dashboard.py
calibration:
	python policyengine_us/data/datasets/cps/enhanced_cps/run_calibration.py
clear-storage:
	rm -f policyengine_us/data/storage/*.h5
	rm -f policyengine_us/data/storage/*.csv.gz
	rm -rf policyengine_us/data/storage/*cache

# Run tests only for changed files
test-changed:
	@echo "Running tests for changed files..."
	@python policyengine_us/tests/run_selective_tests.py --verbose --debug