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

from policyengine_us.tools.section_911 import SECTION_911_LEAF_INPUTS
from policyengine_us.tools.state_eitc_helpers import eitc_filing_status_eligible
from policyengine_us.variables.gov.irs.credits.earned_income.eligibility.eitc_marital_eligible import (
    eitc_marital_eligible,
)
from policyengine_us.variables.gov.states.nj.tax.income.credits.eitc.nj_childless_eitc_age_eligible import (
    nj_childless_eitc_age_eligible,
)
from policyengine_us.variables.gov.states.nj.tax.income.credits.eitc.nj_eitc import (
    nj_eitc,
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
    possible_values = SimpleNamespace(
        SEPARATE="SEPARATE", JOINT="JOINT", HEAD_OF_HOUSEHOLD="HEAD_OF_HOUSEHOLD"
    )


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
        # The first member of each unit is the filer; nobody is separated, so
        # the separated head-of-household route is not exercised here.
        filer = np.r_[True, self.member_groups[1:] != self.member_groups[:-1]]
        self.person_values["is_tax_unit_head_or_spouse"] = filer
        self.person_values["is_separated"] = np.zeros_like(filer)
        self.person_values["is_separated_under_decree"] = np.zeros_like(filer)
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


# IRC 7703(a)(2): a filer legally separated under a decree of separate
# maintenance is not married, so IRC 32(d) needs no exception for the unit.
DECREE_STATUSES = ("SEPARATE", "HEAD_OF_HOUSEHOLD", "JOINT", "SINGLE")
DECREE_HOLDERS = ("nobody", "head", "dependent")


class DecreeUnits:
    """Units over status, head separation, separation facts and decree holder.

    Each generated child list is crossed with every status, head is_separated
    value, separation-fact pair and decree holder. Members are the head, then
    one dependent who never counts as a qualifying child, then the children.
    """

    def __init__(self, cases):
        member_groups, person_rows, unit_rows = [], [], []
        for case_index, case in enumerate(cases):
            for status, separated, (apart, legal), holder in product(
                DECREE_STATUSES, (False, True), SEPARATION_FACTS, DECREE_HOLDERS
            ):
                unit_index = len(unit_rows)
                unit_rows.append(
                    (
                        case_index,
                        status,
                        separated,
                        apart,
                        legal,
                        DECREE_HOLDERS.index(holder),
                    )
                )
                # (head_or_spouse, separated, decree, qualifies, resident)
                members = [
                    (True, separated, holder == "head", False, True),
                    (False, False, holder == "dependent", False, True),
                    *[(False, False, False, q, r) for q, r in case],
                ]
                member_groups.extend([unit_index] * len(members))
                person_rows.extend(members)
        self.member_groups = np.asarray(member_groups, dtype=int)
        self.count = len(unit_rows)
        columns = np.asarray(person_rows, dtype=bool).T
        self.person_values = dict(
            zip(
                (
                    "is_tax_unit_head_or_spouse",
                    "is_separated",
                    "is_separated_under_decree",
                    "is_eitc_qualifying_child",
                    "eitc_child_lived_with_taxpayer_more_than_half_year",
                ),
                columns,
            )
        )
        case_index, status, separated, apart, legal, holder = zip(*unit_rows)
        self.case_index = np.asarray(case_index)
        self.status = np.asarray(status)
        self.separated = np.asarray(separated)
        self.holder = np.asarray(holder)
        self.values = {
            "filing_status": np.asarray(status).view(FilingStatuses),
            "eitc_spouses_lived_apart_last_six_months": np.asarray(apart),
            "eitc_legal_separation_and_apart_at_year_end": np.asarray(legal),
        }

    def __call__(self, variable, period):
        return self.values[variable]

    def members(self, variable, period):
        return self.person_values[variable]

    def any(self, values):
        result = np.zeros(self.count, dtype=bool)
        np.logical_or.at(result, self.member_groups, values)
        return result


def head_rule_without_decree(units, has_resident_child, year):
    """IRC 32(d) as this PR read it before the decree input existed.

    Written from the statute rather than copied from the formula: before 2021
    a separate return is barred; from 2021 a separate filer, or a separated
    head of household, needs a resident qualifying child and either route.
    """
    separate = units.status == "SEPARATE"
    if year < 2021:
        return ~separate
    needs_exception = separate | (
        (units.status == "HEAD_OF_HOUSEHOLD") & units.separated
    )
    routes = (
        units.values["eitc_spouses_lived_apart_last_six_months"]
        | units.values["eitc_legal_separation_and_apart_at_year_end"]
    )
    return ~needs_exception | (has_resident_child[units.case_index] & routes)


@settings(max_examples=50, deadline=None, derandomize=True)
@given(
    cases=st.lists(
        st.lists(st.tuples(st.booleans(), st.booleans()), max_size=3),
        min_size=1,
        max_size=6,
    )
)
@example(cases=[[], [(True, True)], [(True, False)]])
def test_decree_of_separate_maintenance_invariants(cases):
    units = DecreeUnits(cases)
    has_resident_child = np.asarray([any(q and r for q, r in case) for case in cases])
    nobody, head, dependent = (
        units.holder == DECREE_HOLDERS.index(h) for h in DECREE_HOLDERS
    )
    for year in (2020, 2021, 2025):
        actual = eitc_marital_eligible.formula(units, f"{year}-01-01", parameters)
        expected = head_rule_without_decree(units, has_resident_child, year)

        # With the decree input false everywhere, results equal the rule
        # before the input existed, and a decree on a dependent changes
        # nothing: only the head or spouse can be separated under a decree.
        np.testing.assert_array_equal(actual[nobody], expected[nobody])
        np.testing.assert_array_equal(actual[dependent], expected[dependent])
        # Turning the decree input on never removes marital eligibility.
        assert np.all(actual[nobody] <= actual[head])
        if year < 2021:
            # The frozen pre-ARPA path ignores the input.
            np.testing.assert_array_equal(actual[head], actual[nobody])
        else:
            # A decree makes the head unmarried, whatever the other facts.
            assert actual[head].all()
            # Not vacuous: every case has a separate filer with no separation
            # route who fails without the decree and passes with it.
            gained = actual[head] & ~actual[nobody]
            assert set(units.case_index[head][gained]) == set(range(len(cases)))

    # States that freeze the exception off keep barring separate returns.
    frozen = eitc_filing_status_eligible(
        units, "2025-01-01", parameters, separate_filer_eligible=False
    )
    np.testing.assert_array_equal(frozen, units.status != "SEPARATE")


NJ_EITC = ParameterNode(
    "eitc",
    directory_path=str(
        Path(__file__).resolve().parents[1]
        / "parameters/gov/states/nj/tax/income/credits/eitc"
    ),
)
FEDERAL_EITC = ParameterNode(
    "eitc",
    directory_path=str(
        Path(__file__).resolve().parents[1] / "parameters/gov/irs/credits/eitc"
    ),
)


def nj_parameters(period):
    return SimpleNamespace(
        gov=SimpleNamespace(
            irs=SimpleNamespace(credits=SimpleNamespace(eitc=FEDERAL_EITC(period))),
            states=SimpleNamespace(
                nj=SimpleNamespace(
                    tax=SimpleNamespace(
                        income=SimpleNamespace(
                            credits=SimpleNamespace(eitc=NJ_EITC(period))
                        )
                    )
                )
            ),
        )
    )


class NewJerseyUnits:
    """One-person New Jersey units with federal EITC results as inputs."""

    def __init__(self, rows, marital):
        (
            age,
            child_count,
            income_eligible,
            other_federal_eligible,
            phased_in,
            reduction,
            takes_up,
        ) = (np.asarray(column) for column in zip(*rows))
        marital = np.asarray(marital, dtype=bool)
        # eitc_eligible includes the marital condition.
        eligible = np.asarray(other_federal_eligible, dtype=bool) & marital
        self.count = len(rows)
        self.person_values = {"age": age}
        zeros = np.zeros(self.count)
        self.values = {
            "eitc_marital_eligible": marital,
            "eitc_child_count": child_count,
            "nj_eitc_income_eligible": np.asarray(income_eligible, dtype=bool),
            "eitc_eligible": eligible,
            "eitc_phased_in": phased_in,
            "eitc_reduction": reduction,
            "takes_up_eitc": np.asarray(takes_up, dtype=bool),
            "eitc": np.maximum(phased_in - reduction, 0) * eligible * takes_up,
            "foreign_earned_income_exclusion": zeros,
            "section_911_excluded_income": zeros,
        }
        for variable in SECTION_911_LEAF_INPUTS:
            self.values[variable] = zeros

    def __call__(self, variable, period):
        return self.values[variable]

    def members(self, variable, period):
        return self.person_values[variable]

    def any(self, values):
        return np.asarray(values, dtype=bool)


def nj_eitc_for(rows, marital, year):
    units = NewJerseyUnits(rows, marital)
    period = f"{year}-01-01"
    units.values["nj_childless_eitc_age_eligible"] = (
        nj_childless_eitc_age_eligible.formula(units, period, nj_parameters)
    )
    return nj_eitc.formula(units, period, nj_parameters)


nj_rows = st.tuples(
    st.integers(15, 80),
    st.integers(0, 2),
    st.booleans(),
    st.booleans(),
    st.floats(0, 8_000),
    st.floats(0, 8_000),
    st.booleans(),
)


@settings(max_examples=50, deadline=None, derandomize=True)
@given(
    rows=st.lists(nj_rows, min_size=1, max_size=20),
    marital=st.lists(st.booleans(), min_size=20, max_size=20),
)
@example(
    rows=[(22, 0, True, False, 612.0, 0.0, True)] * 2,
    marital=[False, True] + [False] * 18,
)
def test_nj_eitc_requires_federal_marital_eligibility(rows, marital):
    marital = marital[: len(rows)]
    for year in (2021, 2025):
        actual = nj_eitc_for(rows, marital, year)
        # A unit that fails the federal marital test gets no NJ EITC, either
        # through the federal match or the age fallback.
        assert np.all(actual[~np.asarray(marital)] == 0)
        # Not vacuous: with the marital test passed, the age fallback pays a
        # childless filer aged 18 or more who meets the income tests.
        passed = nj_eitc_for(rows, [True] * len(rows), year)
        age, children, income_ok, _, phased_in, reduction, _ = (
            np.asarray(column) for column in zip(*rows)
        )
        fallback = (age >= 18) & (children == 0) & income_ok & (phased_in > reduction)
        assert np.all(passed[fallback] > 0)
