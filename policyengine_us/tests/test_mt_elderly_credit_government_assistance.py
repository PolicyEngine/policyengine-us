"""Property tests: government assistance in the Montana elderly
homeowner/renter credit.

MCA 15-30-2337(9)(a) counts "all nontaxable income, including but not
limited to ... (vi) cash public assistance and relief", and (4) counts "all
income received by all individuals of a household". The 2024 Schedule 2EC
line 16 names "supplemental security income (SSI) payments, worker's
compensation, and any other government assistance"; line 17 carries the same
items for the other members of the household.

The model holds SSI and workers' compensation per person and TANF per SPM
unit, which it spreads over the unit's members (tanf_person). For a claimant
aged 62 or older (taxable pension, SSI, workers' compensation, property tax,
rent) living with another adult (SSI, workers' compensation) and a child,
whose SPM unit receives TANF, in four arrangements:

  A. one return, the other adult and the child the claimant's dependents, and
     one SPM unit;
  B. two returns (the claimant's, and the other adult's with the child) and
     one SPM unit;
  C. two returns and two SPM units, the TANF going to the other adult's;
  D. as C, with more of one kind of assistance;

1. The household's gross household income is the pension plus every
   member's SSI and workers' compensation plus the TANF, once, in A, B and C.
2. So the claimant's credit is the same in A, B and C, and nobody else
   claims.
3. The credit equals an independent reading of Schedule 2EC lines 18 to 30,
   is between zero and the cap, and is zero at $45,000 or more (line 29).
4. More assistance never raises the credit (D against C).

No one has earned income, so no refundable credit enters line 8. The model
computes in single precision, so comparisons allow one cent or eight float32
spacings at the household's total income, whichever is larger.
"""

import numpy as np
import pytest

from policyengine_us import Simulation

YEAR = 2024
CAP = 1_150
INCOME_LIMIT = 45_000
TOLERANCE = 0.01
ARRANGEMENTS = "ABCD"
# 2024 Schedule 2EC, line 19.
EXCLUSION = 12_600
# Household Income Reduction Table (line 21): lower bounds and rates.
REDUCTION_TABLE = [
    (0, 0),
    (2_000, 0.006),
    (3_000, 0.016),
    (4_000, 0.024),
    (5_000, 0.028),
    (6_000, 0.032),
    (7_000, 0.035),
    (8_000, 0.039),
    (9_000, 0.042),
    (10_000, 0.045),
    (11_000, 0.048),
    (12_000, 0.05),
]
# Credit Multiplier Table (line 29): lower bounds of line 18 and percentages.
MULTIPLIER_TABLE = [
    (0, 1),
    (35_000, 0.4),
    (37_501, 0.3),
    (40_001, 0.2),
    (42_501, 0.1),
    (45_000, 0),
]
EXTRA_KINDS = ["claimant_ssi", "member_workers_compensation", "tanf"]


def amounts(c, arrangement):
    """The case's assistance amounts, with D's extra amount added."""
    a = {
        "claimant_ssi": c["claimant_ssi"],
        "claimant_workers_compensation": c["claimant_workers_compensation"],
        "member_ssi": c["member_ssi"],
        "member_workers_compensation": c["member_workers_compensation"],
        "tanf": c["tanf"],
    }
    if arrangement == "D":
        a[c["extra_kind"]] += c["extra"]
    return a


def build_situation(cases):
    people, tax_units, marital_units, spm_units, families, households = (
        {},
        {},
        {},
        {},
        {},
        {},
    )
    for i, c in enumerate(cases):
        for arrangement in ARRANGEMENTS:
            key = f"{arrangement}{i}"
            a = amounts(c, arrangement)
            claimant, member, child = (
                f"claimant_{key}",
                f"member_{key}",
                f"child_{key}",
            )
            people[claimant] = {
                "age": {YEAR: c["claimant_age"]},
                "taxable_pension_income": {YEAR: c["pension"]},
                "ssi": {YEAR: a["claimant_ssi"]},
                "workers_compensation": {YEAR: a["claimant_workers_compensation"]},
                "real_estate_taxes": {YEAR: c["property_tax"]},
                "rent": {YEAR: c["rent"]},
                "is_tax_unit_dependent": {YEAR: False},
            }
            people[member] = {
                "age": {YEAR: c["member_age"]},
                "ssi": {YEAR: a["member_ssi"]},
                "workers_compensation": {YEAR: a["member_workers_compensation"]},
                "is_tax_unit_dependent": {YEAR: arrangement == "A"},
            }
            people[child] = {
                "age": {YEAR: c["child_age"]},
                "is_tax_unit_dependent": {YEAR: True},
            }
            if arrangement == "A":
                tax_units[f"tax_unit_{key}"] = {"members": [claimant, member, child]}
            else:
                tax_units[f"tax_unit_{key}"] = {"members": [claimant]}
                tax_units[f"tax_unit_{key}_member"] = {"members": [member, child]}
            if arrangement in "AB":
                spm_units[f"spm_unit_{key}"] = {
                    "members": [claimant, member, child],
                    "tanf": {YEAR: a["tanf"]},
                }
            else:
                spm_units[f"spm_unit_{key}"] = {
                    "members": [claimant],
                    "tanf": {YEAR: 0},
                }
                spm_units[f"spm_unit_{key}_member"] = {
                    "members": [member, child],
                    "tanf": {YEAR: a["tanf"]},
                }
            for person in (claimant, member, child):
                marital_units[f"marital_unit_{person}"] = {"members": [person]}
            families[f"family_{key}"] = {"members": [claimant, member, child]}
            households[f"household_{key}"] = {
                "members": [claimant, member, child],
                "state_code": {YEAR: "MT"},
            }
    return {
        "people": people,
        "tax_units": tax_units,
        "marital_units": marital_units,
        "spm_units": spm_units,
        "families": families,
        "households": households,
    }


def calculate(cases):
    """Household totals of gross household income and the credit, and the
    other members' credits, as arrays indexed [arrangement, case]."""
    simulation = Simulation(situation=build_situation(cases))
    n, k = len(cases), len(ARRANGEMENTS)

    def by_household(variable):
        values = simulation.calculate(variable, YEAR, map_to="household")
        return np.asarray(values).reshape(n, k).T

    person_credit = np.asarray(
        simulation.calculate("mt_elderly_homeowner_or_renter_credit", YEAR)
    ).reshape(n, k, 3)
    return {
        "gross_household_income": by_household(
            "mt_elderly_homeowner_or_renter_credit_gross_household_income"
        ),
        "credit": by_household("mt_elderly_homeowner_or_renter_credit"),
        # The other adult's and the child's credits.
        "others_credit": person_credit[:, :, 1:].transpose(1, 0, 2),
    }


def expected_gross_household_income(c, arrangement):
    """2024 Schedule 2EC line 18: line 5 pension and line 16 assistance for
    the claimant, line 17 the other members' assistance, the TANF once."""
    return c["pension"] + sum(amounts(c, arrangement).values())


def lookup(table, amount):
    rate = 0
    for lower, value in table:
        if amount >= lower:
            rate = value
    return rate


def expected_credit(c, gross_household_income):
    """2024 Schedule 2EC lines 19 to 30 for a claimant who owns or rents."""
    line_20 = max(gross_household_income - EXCLUSION, 0)
    line_22 = line_20 * lookup(REDUCTION_TABLE, line_20)
    line_26 = c["property_tax"] + 0.15 * c["rent"]
    line_27 = max(line_26 - line_22, 0)
    line_28 = min(line_27, CAP)
    return line_28 * lookup(MULTIPLIER_TABLE, gross_household_income)


def tolerance(amount):
    return max(TOLERANCE, 8 * float(np.spacing(np.float32(abs(amount)))))


def assert_properties(cases):
    result = calculate(cases)
    ghi, credit = result["gross_household_income"], result["credit"]
    for i, c in enumerate(cases):
        for j, arrangement in enumerate(ARRANGEMENTS):
            expected = expected_gross_household_income(c, arrangement)
            tol = tolerance(expected)
            # 1. Every member's assistance counts, the TANF once.
            assert ghi[j, i] == pytest.approx(expected, abs=tol), (arrangement, c)
            # 3. The schedule, the bounds and the income limit.
            assert credit[j, i] == pytest.approx(
                expected_credit(c, expected), abs=tol
            ), (arrangement, c)
            assert -tol <= credit[j, i] <= CAP + tol, (arrangement, c)
            if expected >= INCOME_LIMIT:
                assert credit[j, i] == 0, (arrangement, c)
        # 2. The arrangement does not change the credit, and only the
        # claimant claims.
        tol = tolerance(expected_gross_household_income(c, "D"))
        assert credit[1, i] == pytest.approx(credit[0, i], abs=tol), c
        assert credit[2, i] == pytest.approx(credit[0, i], abs=tol), c
        assert np.all(result["others_credit"][:, i] == 0), c
        # 4. More assistance never raises the credit.
        assert credit[3, i] <= credit[2, i] + tol, c


def test_worked_example():
    """2024 Schedule 2EC: line 5 pension 20,000; line 16 the claimant's SSI
    3,000; line 17 the other adult's SSI 2,000 and workers' compensation
    1,000 and the TANF 1,800; line 18 = 27,800; line 22 = (27,800 - 12,600)
    x 0.05 = 760; line 27 = 1,500 - 760 = 740; line 30 = 740 in A, B and C.
    D adds 8,000 of TANF: line 18 = 35,800; line 22 = 1,160; line 27 = 340;
    line 29 = 40%; line 30 = 136."""
    case = {
        "claimant_age": 70,
        "pension": 20_000,
        "claimant_ssi": 3_000,
        "claimant_workers_compensation": 0,
        "property_tax": 1_500,
        "rent": 0,
        "member_age": 35,
        "member_ssi": 2_000,
        "member_workers_compensation": 1_000,
        "child_age": 6,
        "tanf": 1_800,
        "extra_kind": "tanf",
        "extra": 8_000,
    }
    result = calculate([case])
    assert result["gross_household_income"][:, 0] == pytest.approx(
        [27_800, 27_800, 27_800, 35_800], abs=TOLERANCE
    )
    assert result["credit"][:, 0] == pytest.approx(
        [740, 740, 740, 136], abs=TOLERANCE
    )
    assert_properties([case])


try:
    import hypothesis
    import hypothesis.strategies as st
except ImportError:  # pragma: no cover
    hypothesis = None

if hypothesis is not None:
    # Each example builds a Simulation; on a loaded runner input generation
    # can trip the too_slow health check, which says nothing about the model.
    SLOW = [hypothesis.HealthCheck.too_slow]

    def amount(high):
        return st.one_of(st.just(0), st.integers(min_value=1, max_value=high))

    @st.composite
    def case(draw):
        return {
            "claimant_age": draw(st.integers(min_value=62, max_value=90)),
            "pension": draw(amount(40_000)),
            "claimant_ssi": draw(amount(12_000)),
            "claimant_workers_compensation": draw(amount(15_000)),
            "property_tax": draw(st.integers(min_value=0, max_value=4_000)),
            "rent": draw(amount(12_000)),
            "member_age": draw(st.integers(min_value=18, max_value=61)),
            "member_ssi": draw(amount(12_000)),
            "member_workers_compensation": draw(amount(15_000)),
            "child_age": draw(st.integers(min_value=0, max_value=17)),
            "tanf": draw(amount(10_000)),
            "extra_kind": draw(st.sampled_from(EXTRA_KINDS)),
            "extra": draw(st.integers(min_value=1, max_value=20_000)),
        }

    @hypothesis.settings(max_examples=15, deadline=None, suppress_health_check=SLOW)
    @hypothesis.given(st.lists(case(), min_size=1, max_size=8))
    def test_properties(cases):
        assert_properties(cases)
