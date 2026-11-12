"""Keep Montana filing choices stable within one cent.

Spouses may choose a joint return or separate returns on the same form.
PolicyEngine keeps the joint path when the savings do not exceed one cent.
The rebate base repeats this election before refundable credits, so both
comparisons must make the same choice when credits are zero.
"""

import numpy as np
from hypothesis import given, settings, strategies as st

from policyengine_us import Simulation


@settings(max_examples=4, deadline=None)
@given(
    columns=st.lists(
        st.tuples(st.integers(0, 20_000), st.integers(0, 20_000)),
        min_size=1,
        max_size=4,
    ),
    year=st.sampled_from([2021, 2022, 2023, 2024]),
)
def test_filing_ties_and_rebate_base_agree(columns, year):
    people, tax_units, households = {}, {}, {}
    expected_separate, expected_tax, expected_rebate_base = [], [], []
    # These savings surround one cent and have exact float32 representations.
    savings_grid = [-0.015625, -0.0078125, 0, 0.0078125, 0.015625]
    for i, (head_quarters, spouse_quarters) in enumerate(columns):
        for j, savings in enumerate(savings_grid):
            head_tax, spouse_tax = head_quarters / 4, spouse_quarters / 4
            separate_tax = head_tax + spouse_tax
            joint_tax = max(0, separate_tax + savings)
            separate = year < 2024 and savings == 0.015625
            # Swapping the columns must preserve the election and total tax.
            for swapped in [False, True]:
                key = f"{i}_{j}_{int(swapped)}"
                head, spouse = f"head_{key}", f"spouse_{key}"
                first, second = (
                    (spouse_tax, head_tax) if swapped else (head_tax, spouse_tax)
                )
                people[head] = {
                    "is_tax_unit_head": {year: True},
                    "mt_income_tax_indiv": {year: first},
                    "mt_income_tax_before_refundable_credits_indiv": {year: first},
                }
                people[spouse] = {
                    "is_tax_unit_spouse": {year: True},
                    "mt_income_tax_indiv": {year: second},
                    "mt_income_tax_before_refundable_credits_indiv": {year: second},
                }
                tax_units[key] = {
                    "members": [head, spouse],
                    "mt_income_tax_joint": {year: joint_tax},
                    "mt_income_tax_before_refundable_credits_joint": {year: joint_tax},
                }
                households[key] = {
                    "members": [head, spouse],
                    "state_code": {year: "MT"},
                }
                expected_separate.append(separate)
                expected_tax.append(separate_tax if separate else joint_tax)
                expected_rebate_base.extend(
                    [first, second] if separate else [joint_tax / 2, joint_tax / 2]
                )
    simulation = Simulation(
        situation={
            "people": people,
            "tax_units": tax_units,
            "households": households,
        }
    )
    np.testing.assert_array_equal(
        simulation.calculate("mt_files_separately", year), expected_separate
    )
    np.testing.assert_allclose(
        simulation.calculate("mt_income_tax", year), expected_tax, atol=0, rtol=0
    )
    np.testing.assert_allclose(
        simulation.calculate("mt_income_tax_before_refundable_credits_unit", year),
        expected_tax,
        atol=0,
        rtol=0,
    )
    np.testing.assert_allclose(
        simulation.calculate("mt_income_tax_before_2021_rebate", year),
        expected_rebate_base,
        atol=0,
        rtol=0,
    )
