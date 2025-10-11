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
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/contrib
test-yaml-no-structural:
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline --batches 2
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/household --batches 1
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/baseline/contrib --batches 1
	python policyengine_us/tests/test_batched.py policyengine_us/tests/policy/reform --batches 1
test-other:
	pytest policyengine_us/tests/ --maxfail=0
coverage:
	coverage combine
	coverage xml -i
documentation:
	rm -rf docs/_build
	rm -rf docs/policy/parameters/*
	rm -rf docs/variables/*
	python docs/scripts/generate_docs.py
	cd docs && myst build --site
	python policyengine_us/tools/add_plotly_to_book.py docs/_build/site
	python docs/scripts/generate_latex_paper.py

documentation-install-latex:
	@echo "Checking for required LaTeX packages..."
	@if ! kpsewhich enumitem.sty > /dev/null 2>&1; then \
		echo "Installing enumitem LaTeX package..."; \
		echo "Please run: sudo tlmgr install enumitem"; \
		echo "Or install full MacTeX from https://www.tug.org/mactex/"; \
		exit 1; \
	else \
		echo "✓ enumitem.sty found"; \
	fi
	@if ! kpsewhich fancyhdr.sty > /dev/null 2>&1; then \
		echo "Installing fancyhdr LaTeX package..."; \
		echo "Please run: sudo tlmgr install fancyhdr"; \
		exit 1; \
	else \
		echo "✓ fancyhdr.sty found"; \
	fi
	@echo "All required LaTeX packages are installed!"

documentation-with-latex-check: documentation-install-latex documentation

serve-docs:
	cd docs && myst start
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