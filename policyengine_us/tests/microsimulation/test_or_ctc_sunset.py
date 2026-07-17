"""Microsimulation-level regression test for the Oregon Kids' Credit sunset.

The or_ctc formula must return zero from 2029 (HB 3235 Section 11) so
household-level results match society-wide aggregates (issue #9074).
"""


def test_or_ctc_zero_from_2029():
    from policyengine_us import Microsimulation

    sim = Microsimulation(
        dataset="hf://policyengine/policyengine-us-data/enhanced_cps_2024.h5"
    )
    # Subsampling is seeded by the dataset name, so this is deterministic.
    sim.subsample(10_000)
    # Guard against a vacuous pass: the subsample must contain households
    # actually receiving the credit in the last pre-sunset year.
    assert sim.calc("or_ctc", period=2028).sum() > 0
    assert sim.calc("or_ctc", period=2029).sum() == 0
