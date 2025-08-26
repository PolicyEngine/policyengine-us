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

test-isolated:
	@echo "Running ALL tests with memory isolation..."
	@if [ -f scripts/test_baseline_batched.py ]; then \
		echo "Running baseline tests with batched execution..."; \
		python scripts/test_baseline_batched.py --batch-size 50; \
	fi
	@echo "Running other Python tests..."
	pytest policyengine_us/tests/ --maxfail=0
	@echo "Running reform tests..."
	coverage run -a --branch --data-file=.coverage.reform -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/reform -c policyengine_us
	@if [ -f scripts/test_contrib_isolated.py ]; then \
		echo "Running contrib tests with isolation..."; \
		python scripts/test_contrib_isolated.py --timeout-minutes 10; \
	fi
	coverage xml -i

# Optimized test commands with memory management
test-optimized:
	@echo "Running tests with memory optimization..."
	pytest policyengine_us/tests/ --maxfail=0 --cleanup-frequency=5 --memory-limit=3000
	python scripts/batch_test_runner.py --batch-size=20 --cleanup-frequency=3

test-batch:
	@echo "Running YAML tests in batches (memory efficient)..."
	python scripts/batch_test_runner.py --path policyengine_us/tests/policy/baseline --batch-size=20
test-yaml-structural:
	@echo "Running contrib tests with memory isolation to prevent OOM errors..."
	@if [ -f scripts/test_contrib_isolated.py ]; then \
		python scripts/test_contrib_isolated.py --timeout-minutes 10; \
	else \
		coverage run -a --branch --data-file=.coverage.contrib -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/contrib -c policyengine_us; \
	fi 
test-yaml-no-structural:
	@echo "Running baseline tests with batched memory cleanup (every 50 tests)..."
	@if [ -f scripts/test_baseline_batched.py ]; then \
		python scripts/test_baseline_batched.py --batch-size 50; \
	elif [ -f scripts/test_baseline_isolated.py ]; then \
		python scripts/test_baseline_isolated.py --timeout 120; \
	else \
		coverage run -a --branch --data-file=.coverage.baseline -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/baseline -c policyengine_us; \
	fi
	coverage run -a --branch --data-file=.coverage.reform -m policyengine_core.scripts.policyengine_command test policyengine_us/tests/policy/reform -c policyengine_us

# Memory-efficient version of structural tests
test-yaml-no-structural-optimized:
	@echo "Running baseline tests with memory optimization..."
	python scripts/batch_test_runner.py --path policyengine_us/tests/policy/baseline --batch-size=30 --cleanup-frequency=2
	python scripts/batch_test_runner.py --path policyengine_us/tests/policy/reform --batch-size=30 --cleanup-frequency=2
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

# Add these targets to your existing Makefile

# Run tests only for changed files
test-changed:
	@echo "Running tests for changed files..."
	@python policyengine_us/tests/run_selective_tests.py --verbose --debug