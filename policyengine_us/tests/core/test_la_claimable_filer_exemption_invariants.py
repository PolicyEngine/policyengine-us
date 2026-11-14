"""Check Louisiana's retained exemption reading for claimable filers.

Compare ordinary filers with claimable filers whose claimants do or do not
meet the filing exception. Each batch covers every filing status and zero
through four dependents, with generated ages below the aged-exemption limit.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

YEARS = (2021, 2022, 2023, 2024)
STATUSES = (
    "SINGLE",
    "SEPARATE",
    "SURVIVING_SPOUSE",
    "HEAD_OF_HOUSEHOLD",
    "JOINT",
)


def _situation(year, head_age, spouse_age, child_ages):
    people = {}
    groups = {
        name: {}
        for name in (
            "tax_units",
            "households",
            "families",
            "spm_units",
            "marital_units",
        )
    }
    rows = []

    def add_person(name, age, role, claimable=False, exception=False):
        inputs = {
            "age": age,
            "is_blind": False,
            "is_tax_unit_head": role == "head",
            "is_tax_unit_spouse": role == "spouse",
            "is_tax_unit_dependent": role == "dependent",
            "claimable_as_dependent_on_another_return": claimable,
            "dependent_claimant_filing_exception": exception,
        }
        people[name] = {variable: {year: value} for variable, value in inputs.items()}

    for status in STATUSES:
        variants = [
            ("ordinary", None, False),
            ("blocked_head", "head", False),
            ("except_head", "head", True),
        ]
        if status == "JOINT":
            variants += [
                ("blocked_spouse", "spouse", False),
                ("except_spouse", "spouse", True),
            ]
        for dependents in range(5):
            for variant, claimable_role, exception in variants:
                index = len(rows)
                head = f"head_{index}"
                add_person(
                    head,
                    head_age,
                    "head",
                    claimable_role == "head",
                    exception and claimable_role == "head",
                )
                members = [head]
                couple = [head]
                if status == "JOINT":
                    spouse = f"spouse_{index}"
                    add_person(
                        spouse,
                        spouse_age,
                        "spouse",
                        claimable_role == "spouse",
                        exception and claimable_role == "spouse",
                    )
                    members.append(spouse)
                    couple.append(spouse)
                groups["marital_units"][f"couple_{index}"] = {"members": couple}
                for child_index, age in enumerate(child_ages[:dependents]):
                    child = f"child_{index}_{child_index}"
                    add_person(child, age, "dependent")
                    members.append(child)
                    groups["marital_units"][child] = {"members": [child]}
                groups["tax_units"][f"tax_unit_{index}"] = {
                    "members": members,
                    "filing_status": {year: status},
                }
                groups["households"][f"household_{index}"] = {
                    "members": members,
                    "state_code": {year: "LA"},
                }
                for group in ("families", "spm_units"):
                    groups[group][f"{group}_{index}"] = {"members": members}
                rows.append((status, dependents, variant))
    return {"people": people, **groups}, rows


@pytest.mark.parametrize("year", YEARS)
@settings(
    max_examples=2,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    head_age=st.integers(18, 64),
    spouse_age=st.integers(18, 64),
    child_ages=st.lists(st.integers(0, 17), min_size=4, max_size=4),
)
def test_la_claimable_filer_exemption_invariants(
    year, head_age, spouse_age, child_ages
):
    situation, rows = _situation(year, head_age, spouse_age, child_ages)
    simulation = Simulation(situation=situation)
    values = {
        variable: np.asarray(simulation.calculate(variable, year))
        for variable in (
            "tax_unit_dependents",
            "la_dependents_exemption",
            "la_personal_exemption",
            "la_blind_exemption",
            "la_aged_exemption",
            "la_exemptions",
        )
    }
    counts = np.array([dependents for _, dependents, _ in rows])
    blocked = np.array([variant.startswith("blocked") for _, _, variant in rows])
    own = np.array(
        [4_500 if status in ("SINGLE", "SEPARATE") else 9_000 for status, _, _ in rows]
    )

    np.testing.assert_array_equal(values["tax_unit_dependents"], counts)
    # Filers keep $1,000 per dependent when no claimant blocks the return.
    dependent_amount = np.where(blocked, 0, counts * 1_000)
    np.testing.assert_array_equal(values["la_dependents_exemption"], dependent_amount)
    # Claimable filers keep the personal amount for their filing status.
    np.testing.assert_array_equal(values["la_personal_exemption"], own)
    np.testing.assert_array_equal(values["la_blind_exemption"], 0)
    np.testing.assert_array_equal(values["la_aged_exemption"], 0)
    np.testing.assert_array_equal(values["la_exemptions"], own + dependent_amount)

    positions = {row: index for index, row in enumerate(rows)}
    for status in STATUSES:
        variants = {variant for row_status, _, variant in rows if row_status == status}
        for variant in variants:
            indices = [positions[(status, count, variant)] for count in range(5)]
            amounts = values["la_dependents_exemption"][indices]
            # Adding a dependent increases an allowed exemption by $1,000.
            increment = 0 if variant.startswith("blocked") else 1_000
            np.testing.assert_array_equal(np.diff(amounts), increment)
            assert (amounts >= 0).all()
            assert (amounts <= counts[indices] * 1_000).all()
        for count in range(5):
            ordinary = positions[(status, count, "ordinary")]
            restored = positions[(status, count, "except_head")]
            np.testing.assert_array_equal(
                values["la_exemptions"][restored], values["la_exemptions"][ordinary]
            )
            if status == "JOINT":
                spouse = positions[(status, count, "except_spouse")]
                np.testing.assert_array_equal(
                    values["la_exemptions"][spouse], values["la_exemptions"][ordinary]
                )
