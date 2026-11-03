"""IRC 32(d) and New Jersey invariants over vectorized tax units.

The tests call the production formulas on small entity proxies with the
real parameters, so they build no model. Each invariant can fail on its
own and carries its reason. The tests compare results across inputs and
do not restate a formula. YAML tests pin the dollar amounts.
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
from policyengine_us.variables.gov.states.nj.tax.income.credits.eitc.nj_eitc_separate_filer_eligible import (
    nj_eitc_separate_filer_eligible,
)

PARAMETERS = Path(__file__).resolve().parents[1] / "parameters/gov"
FEDERAL_EITC = ParameterNode(
    "eitc", directory_path=str(PARAMETERS / "irs/credits/eitc")
)
NJ_EITC = ParameterNode(
    "eitc", directory_path=str(PARAMETERS / "states/nj/tax/income/credits/eitc")
)


def parameters(period):
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


class FilingStatuses(np.ndarray):
    possible_values = SimpleNamespace(
        SEPARATE="SEPARATE",
        JOINT="JOINT",
        HEAD_OF_HOUSEHOLD="HEAD_OF_HOUSEHOLD",
        SINGLE="SINGLE",
    )


class Units:
    """Entity access and group aggregation, with no policy logic."""

    def __init__(self, member_groups, person_values, values):
        self.member_groups = np.asarray(member_groups, dtype=int)
        self.count = int(self.member_groups.max()) + 1
        self.person_values = person_values
        self.values = values

    def __call__(self, variable, period):
        return self.values[variable]

    def members(self, variable, period):
        return self.person_values[variable]

    def any(self, values):
        result = np.zeros(self.count, dtype=bool)
        np.logical_or.at(result, self.member_groups, values)
        return result


STATUSES = ("SEPARATE", "HEAD_OF_HOUSEHOLD", "JOINT", "SINGLE")
HOLDERS = ("nobody", "head", "dependent")
GRID = list(product(STATUSES, (False, True), (False, True), (False, True), HOLDERS))
# Child facts: (qualifying child, resident more than half the year, identified).
child = st.tuples(st.booleans(), st.booleans(), st.booleans())


def federal_units(cases):
    """Cross each child list with every status, head is_separated value,
    separation-fact pair and decree holder. Members are the head, a
    dependent who is never a qualifying child, then the children."""
    groups, people, units = [], [], []
    for case_index, case in enumerate(cases):
        for status, separated, apart, legal, holder in GRID:
            members = [
                (True, separated, holder == "head", False, True, True),
                (False, False, holder == "dependent", False, True, True),
                *[(False, False, False, *facts) for facts in case],
            ]
            groups += [len(units)] * len(members)
            people += members
            units.append((case_index, status, separated, apart, legal, holder))
    names = (
        "is_tax_unit_head_or_spouse",
        "is_separated",
        "is_separated_under_decree",
        "is_eitc_qualifying_child",
        "eitc_child_lived_with_taxpayer_more_than_half_year",
        "meets_eitc_identification_requirements",
    )
    person_values = dict(zip(names, np.asarray(people, dtype=bool).T))
    case_index, status, separated, apart, legal, holder = map(np.asarray, zip(*units))
    identified = (
        person_values["is_eitc_qualifying_child"]
        & person_values["meets_eitc_identification_requirements"]
    )
    values = {
        "filing_status": status.view(FilingStatuses),
        "eitc_spouses_lived_apart_last_six_months": apart,
        "eitc_legal_separation_and_apart_at_year_end": legal,
        # The identification-restricted count, exposed so that reading it in
        # place of pre-identification children fails an invariant below.
        "eitc_child_count": np.bincount(groups, weights=identified),
    }
    facts = SimpleNamespace(
        case=case_index,
        status=status,
        separated=separated,
        apart=apart,
        legal=legal,
        holder=holder,
        resident_child=np.asarray([any(q and r for q, r, _ in case) for case in cases])[
            case_index
        ],
    )
    return Units(groups, person_values, values), facts


def counterpart(facts, field, old, new):
    """Return (i, j) index arrays pairing units that differ only in field."""
    keys = np.rec.fromarrays(
        [
            facts.case,
            facts.status,
            facts.separated,
            facts.apart,
            facts.legal,
            facts.holder,
        ],
        names="case,status,separated,apart,legal,holder",
    )
    lookup = {tuple(k): n for n, k in enumerate(keys.tolist())}
    position = keys.dtype.names.index(field)
    i, j = [], []
    for n, key in enumerate(keys.tolist()):
        if key[position] == old:
            other = list(key)
            other[position] = new
            i.append(n)
            j.append(lookup[tuple(other)])
    return np.asarray(i), np.asarray(j)


@settings(max_examples=40, deadline=None, derandomize=True)
@given(cases=st.lists(st.lists(child, max_size=3), min_size=1, max_size=5))
@example(cases=[[], [(True, True, False)], [(True, False, True)]])
def test_federal_marital_invariants(cases):
    units, f = federal_units(cases)
    separate = f.status == "SEPARATE"
    no_decree = f.holder != "head"
    for year in (2020, 2021, 2025):
        ok = eitc_marital_eligible.formula(units, f"{year}-01-01", parameters)

        # 32(d) reaches only married filers who do not file jointly.
        assert ok[(f.status == "JOINT") | (f.status == "SINGLE")].all()
        # 32(d)(2)(B)(i) needs a qualifying child resident over half the year.
        assert not ok[separate & no_decree & ~f.resident_child].any()
        # 7703(a)(2) reaches the taxpayer only, so a dependent's decree is inert.
        i, j = counterpart(f, "holder", "nobody", "dependent")
        np.testing.assert_array_equal(ok[i], ok[j])
        # Each separation route and the head's decree only relieve the test.
        for field, old, new in (
            ("apart", False, True),
            ("legal", False, True),
            ("holder", "nobody", "head"),
        ):
            i, j = counterpart(f, field, old, new)
            assert np.all(ok[i] <= ok[j])

        if year < 2021:
            # Before ARPA 2021, 32(d) barred every separate return.
            np.testing.assert_array_equal(ok, ~separate)
            continue
        # The exception needs one of the two separation routes.
        assert not ok[separate & no_decree & ~f.apart & ~f.legal].any()
        # Either route passes with a resident child, identified or not:
        # 32(c)(3)(D) limits the credit schedule, not 32(d)(2)(B).
        assert ok[separate & f.resident_child & (f.apart | f.legal)].all()
        # 7703(a)(2): a head separated under a decree is not married.
        assert ok[f.holder == "head"].all()
        # 32(d)(2)(A) uses 7703(a) only, so a separated head of household
        # faces the separate filer's test.
        i, j = counterpart(f, "status", "HEAD_OF_HOUSEHOLD", "SEPARATE")
        hoh_separated = f.separated[i]
        np.testing.assert_array_equal(ok[i][hoh_separated], ok[j][hoh_separated])
        # An unseparated head of household is unmarried and passes.
        assert ok[i][~hoh_separated].all()


@pytest.mark.parametrize("year", [2020, 2025])
def test_state_frozen_switch_sets_only_when_the_exception_applies(year):
    units, f = federal_units([[(True, True, False)], [], [(True, False, True)]])
    period = f"{year}-01-01"
    off = eitc_filing_status_eligible(
        units, period, parameters, separate_filer_eligible=False
    )
    on = eitc_filing_status_eligible(
        units, period, parameters, separate_filer_eligible=True
    )
    # A state that freezes the exception off bars every separate return.
    np.testing.assert_array_equal(off, f.status != "SEPARATE")
    # Switching it on gives the current federal test, whatever the year.
    np.testing.assert_array_equal(
        on, eitc_marital_eligible.formula(units, "2025-01-01", parameters)
    )


def nj_units(rows, marital_eligible):
    """One-person New Jersey units with federal EITC results as inputs."""
    (
        status,
        decree,
        age,
        child_count,
        income_eligible,
        other_federal,
        phased_in,
        reduction,
        takes_up,
    ) = map(np.asarray, zip(*rows))
    marital = np.asarray(marital_eligible, dtype=bool)
    eligible = other_federal.astype(bool) & marital
    zeros = np.zeros(len(rows))
    values = {
        "filing_status": status.view(FilingStatuses),
        "eitc_marital_eligible": marital,
        "eitc_child_count": child_count,
        "nj_eitc_income_eligible": income_eligible.astype(bool),
        "eitc_eligible": eligible,
        "eitc_phased_in": phased_in,
        "eitc_reduction": reduction,
        "takes_up_eitc": takes_up.astype(bool),
        "eitc": np.maximum(phased_in - reduction, 0) * eligible * takes_up,
        "foreign_earned_income_exclusion": zeros,
        "section_911_excluded_income": zeros,
        **{variable: zeros for variable in SECTION_911_LEAF_INPUTS},
    }
    person_values = {
        "age": age,
        "is_tax_unit_head_or_spouse": np.ones(len(rows), dtype=bool),
        "is_separated_under_decree": decree.astype(bool),
    }
    return Units(np.arange(len(rows)), person_values, values)


def nj_eitc_for(rows, marital_eligible, year):
    units = nj_units(rows, marital_eligible)
    period = f"{year}-01-01"
    for variable in (nj_eitc_separate_filer_eligible, nj_childless_eitc_age_eligible):
        units.values[variable.__name__] = variable.formula(units, period, parameters)
    return nj_eitc.formula(units, period, parameters)


nj_row = st.tuples(
    st.sampled_from(STATUSES),
    st.booleans(),
    st.integers(15, 80),
    st.integers(0, 2),
    st.booleans(),
    st.booleans(),
    st.floats(0, 8_000),
    st.floats(0, 8_000),
    st.booleans(),
)


@settings(max_examples=40, deadline=None, derandomize=True)
@given(
    rows=st.lists(nj_row, min_size=1, max_size=20),
    marital=st.lists(st.booleans(), min_size=20, max_size=20),
)
@example(
    rows=[
        ("SEPARATE", False, 22, 0, True, False, 612.0, 0.0, True),
        ("SEPARATE", True, 22, 0, True, False, 612.0, 0.0, True),
    ],
    marital=[True] * 20,
)
def test_nj_eitc_marital_invariants(rows, marital):
    marital = np.asarray(marital[: len(rows)])
    status = np.asarray([row[0] for row in rows])
    decree = np.asarray([row[1] for row in rows])
    relaxed_rows = [("JOINT", *row[1:]) for row in rows]
    for year in (2021, 2025):
        actual = nj_eitc_for(rows, marital, year)
        # P.L.2021, c.130 waives only the federal ages, so a unit that fails
        # 32(d) gets nothing through the match or the age fallback.
        assert np.all(actual[~marital] == 0)
        # N.J.S.A. 54A:4-7a.(3) bars a married separate filer, even one the
        # federal exception admits; a decree makes the filer unmarried.
        assert np.all(actual[(status == "SEPARATE") & ~decree] == 0)
        # Neither rule can raise the credit when it applies.
        relaxed = nj_eitc_for(relaxed_rows, np.ones(len(rows), dtype=bool), year)
        assert np.all(actual <= relaxed)
