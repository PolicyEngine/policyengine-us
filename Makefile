# Shorthand for the batch runner so each target is easier to read.
# --mode per-subdir = each immediate subdir runs in its own subprocess
#                     (loose yamls get a trailing batch). New subdirs
#                     auto-route, no Makefile edit needed.
# --mode per-file   = each yaml runs in its own subprocess. Used for
#                     microsim-heavy folders where one file per subprocess
#                     is needed to keep peak RAM under the 16 GB runner.
#
# Memory layout (round 2), calibrated against measured Linux per-batch
# peak RSS from CI run 28698452678 on 16 GB ubuntu-latest runners:
# every batch targets <= ~8 GB peak so >= ~7 GB stays free for future
# test growth, and --workers 1 everywhere except the partners target
# (its largest batch measured 2.5 GB, so two-wide stays trivially safe).
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
# Contrib states: 4 shards, one batch at a time. test_batched.py packs each
# state's files into batches capped by reform-combo weight (each distinct
# reform combo pins ~1.45 GB in policyengine-core's never-evicted cache),
# so every subprocess stays under ~9 GB predicted peak no matter how many
# reform test files a state accumulates. --workers 1 keeps only one such
# peak resident.
test-yaml-structural-heavy-shard-1:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 1/4 --workers 1
test-yaml-structural-heavy-shard-2:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 2/4 --workers 1
test-yaml-structural-heavy-shard-3:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 3/4 --workers 1
test-yaml-structural-heavy-shard-4:
	$(BATCH) $(TESTS)/policy/contrib/states --batches 1 --shard 4/4 --workers 1
test-yaml-structural-other:
	# Per-subdir so every remaining contrib folder runs in its own subprocess,
	# instead of stacking ~20 light files into one ~13-min catch-all batch that
	# risked the 30-min per-batch timeout on slow runners. ssa is excluded (it
	# has no YAML tests — only a pytest .py run elsewhere). --workers 1 so a
	# single ~1-5 GB peak is resident at a time, leaving headroom for growth.
	$(BATCH) $(TESTS)/policy/contrib --exclude states,ctc,ubi_center,federal,harris,treasury,crfb,congress,refundable_credit_conversion,ssa --mode per-subdir --workers 1
test-yaml-structural-other-shard-2a:
	# ctc is microsim-heavy: per-file isolation frees each ~5 GB peak between
	# files, and --workers 1 keeps only one peak resident at a time.
	$(BATCH) $(TESTS)/policy/contrib/ctc --mode per-file --workers 1
	$(BATCH) $(TESTS)/policy/contrib/ubi_center --batches 1
	$(BATCH) $(TESTS)/policy/contrib/federal --batches 1
test-yaml-structural-other-shard-2b:
	# crfb runs per-file: tax_employer_payroll_tax_percentage peaked 9.6 GB as
	# a single file on CI run 28698452678 and is now split into two ~3-case
	# files so each subprocess stays <= ~5 GB; --workers 1 keeps one peak
	# resident at a time.
	$(BATCH) $(TESTS)/policy/contrib/crfb --mode per-file --workers 1
	$(BATCH) $(TESTS)/policy/contrib/harris --batches 1
	$(BATCH) $(TESTS)/policy/contrib/treasury --batches 1
test-yaml-structural-other-shard-3:
	# refundable_credit_conversion force-applies a reform per case; each distinct
	# gov.contrib.* combination clones the full tax-benefit system (~5 GB peak/
	# file). Per-file isolation frees each peak between files; --workers 1 keeps
	# one peak resident at a time.
	$(BATCH) $(TESTS)/policy/contrib/refundable_credit_conversion --mode per-file --workers 1
test-yaml-structural-congress:
	# One subprocess per congress proposal; new proposals auto-route.
	# --workers 1: congress OOM'd two-wide on CI run 28698452678 — the
	# romney batch alone peaked 7.1 GB.
	$(BATCH) $(TESTS)/policy/contrib/congress --mode per-subdir --workers 1
test-yaml-variables:
	$(BATCH) $(TESTS)/variables --batches 1
test-yaml-no-structural-states:
	# 16 batches (was 8) ~= ~3 states per batch. Both 8-batch state shard
	# jobs OOM'd two-wide on CI run 28698452678 (each ~6-state batch peaks
	# ~8+ GB); halving the batch size at --workers 1 keeps each subprocess
	# <= ~6 GB with >= ~10 GB free for future state growth.
	$(BATCH) $(TESTS)/policy/baseline/gov/states --batches 16 --workers 1
test-yaml-no-structural-other:
	$(BATCH) $(TESTS)/policy/baseline --batches 2 --exclude states
	$(BATCH) $(TESTS)/policy/baseline/household --batches 1
	$(BATCH) $(TESTS)/policy/baseline/contrib --batches 1
	$(BATCH) $(TESTS)/policy/reform --mode per-file
test-yaml-no-structural-other-irs:
	# One subprocess per irs subfolder + trailing batch for loose yamls.
	# --workers 1: the irs/tax batch alone peaked 7.6 GB on CI run
	# 28698452678 — co-scheduling a second batch leaves no headroom.
	$(BATCH) $(TESTS)/policy/baseline/gov/irs --mode per-subdir --workers 1
test-yaml-no-structural-other-household:
	# 4 batches (was 2), --workers 1: a 2-batch half of this folder (incl.
	# the weights/MTR files) peaked 11.8 GB on CI run 28698452678. Quarter
	# batches keep each subprocess <= ~6 GB.
	$(BATCH) $(TESTS)/policy/baseline/household --batches 4 --workers 1
test-yaml-no-structural-other-contrib:
	# ubi_center is microsim-heavy → per-file, one ~4 GB peak at a time.
	$(BATCH) $(TESTS)/policy/baseline/contrib/ubi_center --mode per-file --workers 1
	# baseline/contrib/states peaked 12.2 GB as a single per-subdir batch on
	# CI run 28698452678, and its yamls sit two levels deep (states/ri/*/),
	# so per-subdir here would still yield one big "ri" batch — per-file
	# gives each reform yaml its own subprocess instead.
	$(BATCH) $(TESTS)/policy/baseline/contrib/states --mode per-file --workers 1
	# Other contrib subdirs (biden + any future folder) auto-fan out.
	$(BATCH) $(TESTS)/policy/baseline/contrib --exclude ubi_center,states --mode per-subdir --workers 1
test-yaml-reform:
	# Reforms are force-applied and deepcopy the full parameter tree
	# (~5.5 GB peak/file for ctc_linear_phase_out and winship, measured).
	# Running all files in one subprocess stacks past the 16 GB runner cap
	# → "runner received a shutdown signal". One batch per file frees each
	# peak between files; --workers 1 keeps a single peak resident (even an
	# ~8 GB file runs solo with ~8 GB spare); new reform files auto-route.
	$(BATCH) $(TESTS)/policy/reform --mode per-file --workers 1
test-yaml-no-structural-other-hhs:
	# hhs (~2.7 GB peak) rides along with the baseline-contrib runner,
	# which has spare headroom.
	$(BATCH) $(TESTS)/policy/baseline/gov/hhs --batches 1
# baseline contrib + gov/hhs share one CI runner. policy/reform no longer
# rides along: its per-file peaks (~5.5-8 GB) plus this pair filled a job
# past the safety margin, so reform gets its own runner.
test-yaml-contrib-hhs: test-yaml-no-structural-other-contrib test-yaml-no-structural-other-hhs
test-yaml-no-structural-other-ssa:
	# revenue is heavy enough to need its own 2-batch split. --workers 1:
	# revenue batch 1 peaked 8.5 GB on CI run 28698452678, so it must run
	# solo; other ssa subfolders auto-fan one at a time.
	$(BATCH) $(TESTS)/policy/baseline/gov/ssa/revenue --batches 2 --workers 1
	$(BATCH) $(TESTS)/policy/baseline/gov/ssa --exclude revenue --mode per-subdir --workers 1
test-yaml-no-structural-other-usda:
	# usda (~3 GB peak, ~7 min) rides along with ssa, rebalancing runners.
	$(BATCH) $(TESTS)/policy/baseline/gov/usda --batches 1
test-yaml-no-structural-other-ssa-usda: test-yaml-no-structural-other-ssa test-yaml-no-structural-other-usda
test-yaml-no-structural-other-rest-a:
	# First half of the old "rest" job: four independent folders, one
	# single-batch subprocess each (local/aca/fcc/hud measured <= ~5 GB
	# per batch on CI run 28698452678).
	$(BATCH) $(TESTS)/policy/baseline/gov/local --batches 1
	$(BATCH) $(TESTS)/policy/baseline/gov/aca --batches 1
	$(BATCH) $(TESTS)/policy/baseline/gov/fcc --batches 1
	$(BATCH) $(TESTS)/policy/baseline/gov/hud --batches 1
test-yaml-no-structural-other-rest-b:
	# gov/simulation's 5 files together peaked 12.1 GB on CI run
	# 28698452678 — per-file frees each peak between files.
	$(BATCH) $(TESTS)/policy/baseline/gov/simulation --mode per-file --workers 1
	# All remaining gov/ subdirs (cbo, doe, ed, tax, territories) + any new
	# ones auto-route here, one subprocess each (<= ~5 GB measured); loose
	# gov/*.yaml files get the trailing per-subdir batch.
	$(BATCH) $(TESTS)/policy/baseline/gov --exclude states,irs,ssa,usda,hhs,local,aca,fcc,hud,simulation --mode per-subdir --workers 1
	# calcfunctions, income, parameters + any new top-level baseline/ folder
	# are all light (<2.3 GB peak) — group them into one subprocess instead
	# of paying the ~33s interpreter+system-build startup per folder.
	$(BATCH) $(TESTS)/policy/baseline --exclude gov,household,contrib,partners --batches 1
test-yaml-no-structural-other-partners:
	# Customer/API partner fixtures mirrored from policyengine-household-api.
	# analytics_coverage/edge_cases is ~90% of this job's time as a single
	# batch — fan it out per topic/state folder and run two at a time. Only
	# the invocations change here; partner files themselves are untouched.
	$(BATCH) $(TESTS)/policy/baseline/partners/analytics_coverage/edge_cases/federal --mode per-subdir --workers 2
	$(BATCH) $(TESTS)/policy/baseline/partners/analytics_coverage/edge_cases/state --mode per-subdir --workers 2
	# Safety net: anything added directly under edge_cases/ besides federal
	# and state (currently produces zero batches).
	$(BATCH) $(TESTS)/policy/baseline/partners/analytics_coverage/edge_cases --exclude federal,state --batches 1
	# signatures + anything new under analytics_coverage/ as one batch.
	$(BATCH) $(TESTS)/policy/baseline/partners/analytics_coverage --exclude edge_cases --batches 1
	# amplifi + impactica + my_friend_ben (+ any new partner) in one light batch.
	$(BATCH) $(TESTS)/policy/baseline/partners --exclude analytics_coverage --batches 1
# The old single-process test-other run was OOM-killed at ~94% on CI run
# 28698452678: cumulative RSS from the python tests plus the
# microsimulation suite in one pytest process exceeded the 16 GB runner.
# Two pytest processes (run as two CI jobs) bound each peak separately.
test-other-python:
	pytest policyengine_us/tests/ --maxfail=0 --ignore=$(TESTS)/policy/contrib --ignore=$(TESTS)/microsimulation
test-microsimulation:
	pytest $(TESTS)/microsimulation --maxfail=0
# Local convenience: run both halves back to back.
test-other: test-other-python test-microsimulation
test-policy-contrib-python:
	pytest $$(find $(TESTS)/policy/contrib -name 'test*.py' -print) --maxfail=0
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
