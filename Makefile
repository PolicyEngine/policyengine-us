all: build
format:
	black . -l 79
	linecheck . --fix
install:
	pip install -e .[dev]
test:
	pytest policyengine_us/tests/ --maxfail=0
	coverage run -a --branch -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/ -c policyengine_us
	coverage xml -i
test-yaml-structural:
	coverage run -a --branch --data-file=.coverage.contrib -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/contrib -c policyengine_us 
test-yaml-no-structural:
	coverage run -a --branch --data-file=.coverage.baseline -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/baseline -c policyengine_us
	coverage run -a --branch --data-file=.coverage.reform -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/reform -c policyengine_us
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
	python setup.py sdist bdist_wheel
changelog:
	build-changelog changelog.yaml --output changelog.yaml --update-last-date --start-from 0.0.1 --append-file changelog_entry.yaml
	build-changelog changelog.yaml --org PolicyEngine --repo policyengine-us --output CHANGELOG.md --template .github/changelog_template.md
	bump-version changelog.yaml setup.py
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



# Add these targets to your existing Makefile

# Run tests only for changed files
test-changed:
	@echo "Running tests for changed files..."
	@python run_selective_tests.py --verbose

# Run tests for specific states
test-state:
	@if [ -z "$(STATE)" ]; then \
		echo "Usage: make test-state STATE=ca"; \
		exit 1; \
	fi
	@echo "Running tests for state: $(STATE)"
	@pytest policyengine_us/tests/policy/baseline/gov/states/$(STATE) -v

# Show what tests would run for current changes
test-plan:
	@echo "Test execution plan for current changes:"
	@python run_selective_tests.py --plan

# Run tests for a specific component
test-component:
	@if [ -z "$(COMPONENT)" ]; then \
		echo "Usage: make test-component COMPONENT=irs/credits/ctc"; \
		echo "Available components:"; \
		echo "  - irs/credits/ctc"; \
		echo "  - irs/credits/earned_income"; \
		echo "  - usda/snap"; \
		echo "  - hhs/medicaid"; \
		echo "  - states/<state_abbr>"; \
		exit 1; \
	fi
	@echo "Running tests for component: $(COMPONENT)"
	@pytest policyengine_us/tests/policy/baseline/gov/$(COMPONENT) -v

# Run tests in parallel for better performance
test-parallel:
	@echo "Running all tests in parallel..."
	@pytest policyengine_us/tests -n auto

# Run selective tests in parallel
test-changed-parallel:
	@echo "Running changed tests in parallel..."
	@python run_selective_tests.py --verbose | grep -E "policyengine_us/tests" | xargs pytest -n auto

# Quick smoke test - runs a minimal set of critical tests
test-smoke:
	@echo "Running smoke tests..."
	@pytest policyengine_us/tests/code_health -v
	@pytest policyengine_us/tests/test_variables.py -v

# Run tests with coverage for changed files
test-changed-coverage:
	@echo "Running tests with coverage for changed files..."
	@python run_selective_tests.py --verbose | grep -E "policyengine_us/tests" | xargs pytest --cov=policyengine_us --cov-report=html

.PHONY: test-changed test-state test-plan test-component test-parallel test-changed-parallel test-smoke test-changed-coverage