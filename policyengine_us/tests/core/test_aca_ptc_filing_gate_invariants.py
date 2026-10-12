"""Invariants for the filing gate on the ACA premium tax credit.

`aca_ptc` is the credit for a tax unit that files a return on which it can
claim it (`files_return_for_aca_ptc`): one that files for any reason
(`tax_unit_is_filer`) or that takes up the credit, since a taxpayer who
receives advance payments must file and reconcile them (26 CFR 1.6011-8(a)).
Hypothesis draws tax units with any benchmark premium, household income and
required contribution, and runs each in all four combinations of filing and
take-up, as one simulation per year. For every tax unit:

1. Taking up the credit never lowers `aca_ptc`.
2. For a tax unit that takes up the credit, `aca_ptc` and `assigned_aca_ptc`
   are the same whether or not it would file for another reason.
3. A tax unit that neither files nor takes up the credit gets no `aca_ptc`
   (the filing gate added for IRS filer data).
4. A tax unit that files gets the same `aca_ptc` whether or not it takes up
   the credit.

Why Python: the YAML cases pin one combination each with fixed amounts; this
checks every combination of filing and take-up against drawn benchmark
premiums, incomes and contribution rates in one vectorized simulation, so a
gate that drops the take-up leg, or that makes the credit depend on filing for
a unit that takes it up, fails whatever the amounts. Cost, measured locally
(macOS, shared host): 4.4 s of test calls, 7.5 s in pytest and 26 s wall time
including the model import, peak memory footprint 1.5 GB. It runs in the
`core` group of the rest Python tests.
"""

import numpy as np
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2025, 2026)
# (tax_unit_is_filer, takes_up_aca_if_eligible) for the four copies of a unit.
COMBINATIONS = [(False, False), (False, True), (True, False), (True, True)]

units = st.tuples(
    st.integers(0, 30_000),  # slcsp
    st.integers(0, 120_000),  # aca_magi
    st.sampled_from([0.0, 0.02, 0.04, 0.085, 0.0996]),
)


def simulate(rows):
    people, tax_units, households = {}, {}, {}
    groups = {"marital_units": {}, "spm_units": {}, "families": {}}
    index = 0
    for slcsp, magi, share in rows:
        for files, takes_up in COMBINATIONS:
            person, members = f"person_{index}", [f"person_{index}"]
            people[person] = {
                "age": {year: 40 for year in YEARS},
                "is_aca_ptc_eligible": {year: True for year in YEARS},
            }
            tax_units[f"tax_unit_{index}"] = {
                "members": members,
                "slcsp": {year: slcsp for year in YEARS},
                "aca_magi": {year: magi for year in YEARS},
                "aca_required_contribution_percentage": {year: share for year in YEARS},
                "tax_unit_is_filer": {year: files for year in YEARS},
                "takes_up_aca_if_eligible": {year: takes_up for year in YEARS},
            }
            households[f"household_{index}"] = {
                "members": members,
                "state_code": {year: "TX" for year in YEARS},
            }
            for name in groups:
                groups[name][f"{name}_{index}"] = {"members": members}
            index += 1
    return Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
            **groups,
        }
    )


@settings(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(
    st.lists(units, min_size=4, max_size=24).map(
        # A unit whose credit is positive, so properties 1-4 compare something.
        lambda rows: [(12_000, 30_000, 0.04), *rows]
    )
)
def test_aca_ptc_filing_gate(rows):
    simulation = simulate(rows)
    for year in YEARS:
        ptc = np.asarray(simulation.calculate("aca_ptc", year)).reshape(-1, 4)
        assigned = np.asarray(simulation.calculate("assigned_aca_ptc", year)).reshape(
            -1, 4
        )
        neither, takes_up_only, files_only, both = ptc.T
        assert (ptc >= 0).all()
        assert (both > 0).any(), "no unit with a positive credit"
        # Property 1.
        assert (takes_up_only >= neither).all() and (both >= files_only).all()
        # Property 2.
        np.testing.assert_allclose(takes_up_only, both)
        np.testing.assert_allclose(assigned[:, 1], assigned[:, 3])
        # Property 3.
        assert (neither == 0).all()
        # Property 4.
        np.testing.assert_allclose(files_only, both)
