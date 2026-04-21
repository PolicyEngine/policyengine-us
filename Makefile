# Shorthand for the batch runner so each target is easier to read.
# --mode per-subdir = each immediate subdir runs in its own subprocess
#                     (loose yamls get a trailing batch). New subdirs
#                     auto-route, no Makefile edit needed.
# --mode per-file   = each yaml runs in its own subprocess. Used for
#                     microsim-heavy folders where one file per subprocess
#                     is needed to keep peak RAM under the 16 GB runner.
BATCH := python policyengine_us/tests/test_batched.py
TESTS := policyengine_us/tests

all: build
format:
	uv run ruff format .
	uv run ruff check .
install:
	pip install -e .[dev]
test:
	pytest $(TESTS)/ --maxfail=0
	coverage run -a --branch -m policyengine_core.scripts.policyengine_command test $(TESTS)/policy/ -c policyengine_us
	coverage xml -i
test-yaml-structural:
	$(BATCH) $(TESTS)/policy/contrib --exclude states
test-yaml-structural-heavy:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1
test-yaml-structural-heavy-shard-1:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 1/2
test-yaml-structural-heavy-shard-2:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 2/2
test-yaml-structural-other:
	$(BATCH) $(TESTS)/policy/contrib --exclude states,ctc,ubi_center,federal,harris,treasury,crfb,congress
test-yaml-structural-other-shard-2:
	# ctc + crfb are microsim-heavy: per-file isolation keeps RAM under the cap.
	$(BATCH) $(TESTS)/policy/contrib/ctc --mode per-file
	$(BATCH) $(TESTS)/policy/contrib/crfb --mode per-file
	$(BATCH) $(TESTS)/policy/contrib/ubi_center --batches 1
	$(BATCH) $(TESTS)/policy/contrib/federal --batches 1
	$(BATCH) $(TESTS)/policy/contrib/harris --batches 1
	$(BATCH) $(TESTS)/policy/contrib/treasury --batches 1
test-yaml-structural-congress:
	# One subprocess per congress proposal; new proposals auto-route.
	$(BATCH) $(TESTS)/policy/contrib/congress --mode per-subdir
test-yaml-variables:
	$(BATCH) $(TESTS)/variables --batches 1
test-yaml-no-structural-states:
	$(BATCH) $(TESTS)/policy/baseline/gov/states --batches 4 --exclude ny
	$(MAKE) test-yaml-no-structural-states-ny
test-yaml-no-structural-states-ny:
	# NY credits clone the tax_benefit_system per scenario (~12 GB) —
	# split explicitly. Everything else under ny/ auto-fans out.
	$(BATCH) $(TESTS)/policy/baseline/gov/states/ny/tax/income/credits --batches 3
	$(BATCH) $(TESTS)/policy/baseline/gov/states/ny/tax/income/taxable_income --batches 1
	$(BATCH) $(TESTS)/policy/baseline/gov/states/ny/tax/income --exclude credits,taxable_income --batches 1
	$(BATCH) $(TESTS)/policy/baseline/gov/states/ny --exclude tax --mode per-subdir
test-yaml-no-structural-other:
	$(BATCH) $(TESTS)/policy/baseline --batches 2 --exclude states
	$(BATCH) $(TESTS)/policy/baseline/household --batches 1
	$(BATCH) $(TESTS)/policy/baseline/contrib --batches 1
	$(BATCH) $(TESTS)/policy/reform --batches 1
test-yaml-no-structural-other-irs:
	# One subprocess per irs subfolder + trailing batch for loose yamls.
	$(BATCH) $(TESTS)/policy/baseline/gov/irs --mode per-subdir
test-yaml-no-structural-other-household:
	$(BATCH) $(TESTS)/policy/baseline/household --batches 2
test-yaml-no-structural-other-irs-household: test-yaml-no-structural-other-irs test-yaml-no-structural-other-household
test-yaml-no-structural-other-contrib:
	# ubi_center is microsim-heavy → per-file. Other contrib subdirs
	# (biden, states, + any future folder) auto-fan out.
	$(BATCH) $(TESTS)/policy/baseline/contrib/ubi_center --mode per-file
	$(BATCH) $(TESTS)/policy/baseline/contrib --exclude ubi_center --mode per-subdir
test-yaml-reform:
	$(BATCH) $(TESTS)/policy/reform --batches 1
test-yaml-no-structural-other-ssa:
	# revenue is heavy enough to need its own 2-batch split; others auto-fan.
	$(BATCH) $(TESTS)/policy/baseline/gov/ssa/revenue --batches 2
	$(BATCH) $(TESTS)/policy/baseline/gov/ssa --exclude revenue --mode per-subdir
test-yaml-no-structural-other-rest:
	# All remaining gov/ subdirs + any new ones auto-route here.
	$(BATCH) $(TESTS)/policy/baseline/gov --exclude states,irs,ssa --mode per-subdir
	# All top-level baseline/ subdirs except gov/household/contrib
	# (calcfunctions, income, parameters + any new folder) auto-route here.
	$(BATCH) $(TESTS)/policy/baseline --exclude gov,household,contrib --mode per-subdir
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
	python .github/bump_version.py
	towncrier build --yes --version $$(python -c "import re; print(re.search(r'version = \"(.+?)\"', open('pyproject.toml').read()).group(1))")
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
