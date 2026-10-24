"""IRC 32(d) invariants over vectorized tax units and member populations.

Invoke the production marital-eligibility formula with small entity proxies
and the actual exception parameter. Hypothesis varies qualifying-child,
residence and identification facts, while each unit is evaluated with all
four separation-fact combinations as both a separate and a joint filer.
YAML tests cover model integration; these generated populations check
monotonicity and aggregation without constructing or copying full models.
"""

from itertools import product
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters import ParameterNode

from policyengine_us.tools.state_eitc_helpers import eitc_filing_status_eligible
from policyengine_us.variables.gov.irs.credits.earned_income.eligibility.eitc_marital_eligible import (
    eitc_marital_eligible,
)


ELIGIBILITY = ParameterNode(
    "eligibility",
    directory_path=str(
        Path(__file__).resolve().parents[1]
        / "parameters/gov/irs/credits/eitc/eligibility"
    ),
)
SEPARATION_FACTS = list(product((False, True), repeat=2))


def parameters(period):
    return SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(
                credits=SimpleNamespace(
                    eitc=SimpleNamespace(eligibility=ELIGIBILITY(period))
                )
            )
        )
    )


class FilingStatuses(np.ndarray):
    possible_values = SimpleNamespace(SEPARATE="SEPARATE", JOINT="JOINT")


class TaxUnits:
    """Provide entity access and group aggregation, without policy logic."""

    def __init__(self, cases):
        self.member_groups = []
        member_values = []
        statuses, six_months, legal_separation = [], [], []
        for case in cases:
            for status in ("SEPARATE", "JOINT"):
                for apart, legal in SEPARATION_FACTS:
                    unit_index = len(statuses)
                    statuses.append(status)
                    six_months.append(apart)
                    legal_separation.append(legal)
                    # Every unit has an adult as well as its generated members.
                    members = [(False, True, True), *case]
                    self.member_groups.extend([unit_index] * len(members))
                    member_values.extend(members)
        self.member_groups = np.asarray(self.member_groups, dtype=int)
        self.count = len(statuses)
        self.person_values = dict(
            zip(
                (
                    "is_eitc_qualifying_child",
                    "eitc_child_lived_with_taxpayer_more_than_half_year",
                    "meets_eitc_identification_requirements",
                ),
                np.asarray(member_values, dtype=bool).T,
            )
        )
        # Expose the existing SSN-restricted count as well, so accidentally
        # using it instead of pre-identification children fails the properties.
        identified_children = (
            self.person_values["is_eitc_qualifying_child"]
            & self.person_values["meets_eitc_identification_requirements"]
        )
        self.values = {
            "filing_status": np.asarray(statuses).view(FilingStatuses),
            "eitc_spouses_lived_apart_last_six_months": np.asarray(six_months),
            "eitc_legal_separation_and_apart_at_year_end": np.asarray(legal_separation),
            "eitc_child_count": np.bincount(
                self.member_groups,
                weights=identified_children,
                minlength=self.count,
            ),
        }

    def __call__(self, variable, period):
        return self.values[variable]

    def members(self, variable, period):
        return self.person_values[variable]

    def any(self, values):
        result = np.zeros(self.count, dtype=bool)
        np.logical_or.at(result, self.member_groups, values)
        return result


member_facts = st.tuples(st.booleans(), st.booleans(), st.booleans())


@settings(max_examples=50, deadline=None, derandomize=True)
@given(cases=st.lists(st.lists(member_facts, max_size=5), min_size=1, max_size=12))
@example(
    cases=[
        [],
        [(True, True, False)],
        [(True, False, True), (False, True, True)],
    ]
)
def test_marital_eligibility_invariants(cases):
    tax_units = TaxUnits(cases)
    has_resident_child = np.asarray(
        [
            any(qualifies and resident for qualifies, resident, _ in case)
            for case in cases
        ]
    )
    for year in (2020, 2021, 2025):
        actual = eitc_marital_eligible.formula(
            tax_units, f"{year}-01-01", parameters
        ).reshape(len(cases), 2, len(SEPARATION_FACTS))
        separate, joint = actual[:, 0], actual[:, 1]

        # Joint filers satisfy the marital test for every child/separation fact.
        assert joint.all()
        # No child, or only a nonresident child, can never enable the exception.
        assert not separate[~has_resident_child].any()
        # Adding either true separation fact cannot remove eligibility.
        assert np.all(separate[:, 0] <= separate[:, 1])
        assert np.all(separate[:, 0] <= separate[:, 2])
        assert np.all(separate[:, 1] <= separate[:, 3])
        assert np.all(separate[:, 2] <= separate[:, 3])

        if year < 2021:
            assert not separate.any()
        else:
            assert not separate[:, 0].any()
            # Both legal routes work with a resident qualifying child, even
            # when that child's identification fails the federal credit test.
            assert separate[has_resident_child, 1:].all()


@pytest.mark.parametrize("year,frozen_switch", [(2025, False), (2020, True)])
def test_state_frozen_exception_switch_overrides_current_year(year, frozen_switch):
    period = f"{year}-01-01"
    assert ELIGIBILITY(period).separate_filer != frozen_switch
    tax_units = TaxUnits(
        [
            [(True, True, False)],
            [],
            [(True, False, True)],
        ]
    )
    actual = eitc_filing_status_eligible(
        tax_units,
        period,
        parameters,
        separate_filer_eligible=frozen_switch,
    ).reshape(3, 2, len(SEPARATION_FACTS))

    # A frozen switch controls when the exception is available, while the
    # resident-child and separation requirements still apply to both routes.
    np.testing.assert_array_equal(
        actual[0, 0], [False, frozen_switch, frozen_switch, frozen_switch]
    )
    assert not actual[1:, 0].any()
    assert actual[:, 1].all()
