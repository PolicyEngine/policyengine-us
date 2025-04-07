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
compare-speed:
	pip uninstall policyengine-us -y
	pip install policyengine-us
	cd policyengine_us/tools && python speedtest.py
	mv policyengine_us/tools/speedtest.yaml speedtest_old.yaml
	pip install -e .
	cd policyengine_us/tools && python speedtest.py
	mv policyengine_us/tools/speedtest.yaml speedtest_new.yaml
	python .github/compare_speed.py
