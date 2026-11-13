"""Generate deduction invariants through an isolated, minimal Core worker.

YAML covers household calculations. These properties compare federal numeric
storage with the former formula and check Minnesota bounds, monotonicity,
historical compatibility and consumers across generated vectors. One module
worker loads actual classes and parameters, then serves requests sequentially.
The fresh worker avoids country startup without changing this interpreter's
imports. It shares this process group and closes before the fixture returns.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from hypothesis import example, given, settings, strategies as st
import pytest


PROPERTY_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    database=None,
    derandomize=True,
)


@pytest.fixture(scope="module")
def invariant_worker():
    worker_path = Path(__file__).with_name("mn_deduction_invariant_checks.py")
    with tempfile.NamedTemporaryFile(
        prefix="mn-deduction-worker-",
        suffix=".log",
        dir=os.environ.get("TMPDIR"),
        delete=False,
    ) as log:
        process = subprocess.Popen(
            [sys.executable, "-u", str(worker_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=log,
            text=True,
            bufsize=1,
        )
        try:

            def response():
                line = process.stdout.readline()
                if not line:
                    detail = Path(log.name).read_text(errors="replace")[-4_000:]
                    raise RuntimeError(
                        f"Invariant worker exited; result inconclusive. {detail}"
                    )
                result = json.loads(line)
                if result["status"] == "error":
                    raise RuntimeError(
                        "Invariant worker error; result inconclusive.\n"
                        + result["traceback"]
                    )
                return result

            ready = response()
            if ready["status"] != "ready":
                raise RuntimeError(f"Invariant worker did not initialize: {ready}")

            def check(name, **arguments):
                process.stdin.write(
                    json.dumps({"check": name, "arguments": arguments}) + "\n"
                )
                process.stdin.flush()
                result = response()
                if result["status"] == "failed":
                    raise AssertionError(result["traceback"])
                if result["status"] != "passed":
                    raise RuntimeError(f"Unexpected invariant response: {result}")

            yield check
        finally:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
            process.stdout.close()


@PROPERTY_SETTINGS
@example(
    agi=100_000,
    donations=(10_000, 5_000, 20_000, 5_000, 15_000, 10_000),
)
@given(
    agi=st.integers(min_value=0, max_value=1_000_000),
    donations=st.tuples(*[st.integers(0, 1_000_000)] * 6),
)
def test_federal_charitable_extraction_preserves_existing_results(
    invariant_worker, agi, donations
):
    invariant_worker("federal", agi=agi, donations=donations)


@PROPERTY_SETTINGS
@example(agi=100_000, contribution=750, increase=1_000)
@example(agi=100_000, contribution=4_000, increase=1)
@given(
    agi=st.integers(min_value=0, max_value=1_000_000),
    contribution=st.integers(min_value=0, max_value=500_000),
    increase=st.integers(min_value=0, max_value=500_000),
)
def test_minnesota_charity_bounds_monotonicity_and_consumers(
    invariant_worker, agi, contribution, increase
):
    invariant_worker("charity", agi=agi, contribution=contribution, increase=increase)


@PROPERTY_SETTINGS
@example(real=15_000, personal=2_000, increase=5_000, historical=10_000)
@given(
    real=st.integers(min_value=0, max_value=100_000),
    personal=st.integers(min_value=0, max_value=100_000),
    increase=st.integers(min_value=0, max_value=100_000),
    historical=st.integers(min_value=0, max_value=100_000),
)
def test_minnesota_property_cap_bounds_statuses_and_historical_compatibility(
    invariant_worker, real, personal, increase, historical
):
    invariant_worker(
        "property",
        real=real,
        personal=personal,
        increase=increase,
        historical=historical,
    )


@PROPERTY_SETTINGS
@example(agi=100_000, contribution=4_000)
@given(
    agi=st.integers(min_value=0, max_value=1_000_000),
    contribution=st.integers(min_value=0, max_value=600_000),
)
def test_minnesota_amt_preserves_federal_charitable_deduction(
    invariant_worker, agi, contribution
):
    invariant_worker("amt", agi=agi, contribution=contribution)
