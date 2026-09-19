"""Maine's standard deduction equals the federal standard deduction from 2027.

36 M.R.S. Sec. 5124-C(1-D), enacted by P.L. 2025, c. 650, Pt. K, Sec. 15
(L.D. 2212): "For tax years beginning on or after January 1, 2027, the standard
deduction of a resident individual is equal to the federal standard deduction,
subject to the phase-out under subsection 2."

These assertions compare Maine's deduction to the federal deduction computed in
the same simulation, so they do not hard code projected federal amounts.
"""

import pytest

from policyengine_us import Simulation
from policyengine_us.system import system as SYSTEM

CONFORMITY_YEARS = (2027, 2028)

SINGLE = {"person": {"age": 40}}
AGED_SINGLE = {"person": {"age": 70}}
JOINT = {
    "person": {"age": 40},
    "spouse": {"age": 38, "is_tax_unit_spouse": True},
}
HEAD_OF_HOUSEHOLD = {
    "person": {"age": 40},
    "child": {"age": 10, "is_tax_unit_dependent": True},
}

# case name: (people, filing status input or None for the default, expected
# filing status of the resulting tax unit)
SITUATIONS = {
    "single": (SINGLE, None, "SINGLE"),
    "aged_single": (AGED_SINGLE, None, "SINGLE"),
    "joint": (JOINT, "JOINT", "JOINT"),
    "head_of_household": (
        HEAD_OF_HOUSEHOLD,
        "HEAD_OF_HOUSEHOLD",
        "HEAD_OF_HOUSEHOLD",
    ),
}


def _simulation(people, filing_status, year, tax_unit_inputs=None):
    period = str(year)
    members = list(people)
    tax_unit = {"members": members}
    if filing_status is not None:
        tax_unit["filing_status"] = {period: filing_status}
    for name, value in (tax_unit_inputs or {}).items():
        tax_unit[name] = {period: value}
    situation = {
        "people": {
            name: {field: {period: value} for field, value in attributes.items()}
            for name, attributes in people.items()
        },
        "tax_units": {"tax_unit": tax_unit},
        "families": {"family": {"members": members}},
        "spm_units": {"spm_unit": {"members": members}},
        "households": {"household": {"members": members, "state_code": {period: "ME"}}},
    }
    return Simulation(situation=situation)


def _maine_own_amount(filing_status, year):
    """Maine's own statutory amounts, which stop being used after 2026."""
    standard = SYSTEM.parameters.gov.states.me.tax.income.deductions.standard
    instant = f"{year}-01-01"
    return standard.amount(instant)[filing_status]


@pytest.mark.parametrize("case", sorted(SITUATIONS))
@pytest.mark.parametrize("year", CONFORMITY_YEARS)
def test_me_standard_deduction_equals_federal_from_2027(case, year):
    people, filing_status, _ = SITUATIONS[case]
    simulation = _simulation(people, filing_status, year)
    period = str(year)
    maine = simulation.calculate("me_standard_deduction", period)[0]
    federal = simulation.calculate("standard_deduction", period)[0]
    assert maine == pytest.approx(federal)
    assert maine > 0


@pytest.mark.parametrize("case", sorted(SITUATIONS))
def test_me_standard_deduction_exceeds_frozen_maine_amount_in_2027(case):
    # Before 36 M.R.S. Sec. 5124-C(1-D) was encoded, Maine's own 2026 amounts
    # were projected forward, which left the 2027 deduction below the federal
    # one. Maine's own amounts are no longer uprated past 2026.
    people, filing_status, expected_status = SITUATIONS[case]
    simulation = _simulation(people, filing_status, 2027)
    maine = simulation.calculate("me_standard_deduction", "2027")[0]
    assert (
        simulation.calculate("filing_status", "2027").decode_to_str()[0]
        == expected_status
    )
    assert maine > _maine_own_amount(expected_status, 2027)
    assert _maine_own_amount(expected_status, 2027) == _maine_own_amount(
        expected_status, 2026
    )


def test_me_standard_deduction_does_not_follow_federal_in_2026():
    # 36 M.R.S. Sec. 5124-C(1-C) fixes Maine's 2026 basic amounts in dollars.
    simulation = _simulation(SINGLE, None, 2026)
    maine = simulation.calculate("me_standard_deduction", "2026")[0]
    federal = simulation.calculate("standard_deduction", "2026")[0]
    assert maine == pytest.approx(15_700)
    assert federal == pytest.approx(16_100)


def test_me_standard_deduction_applies_the_federal_dependent_cap_in_2027():
    # IRC Section 63(c)(5), as adjusted by Rev. Proc. 2025-32 section .14(2):
    # an individual who is a dependent of another taxpayer gets at most the
    # greater of the dependent floor and earned income plus a fixed addition,
    # capped at the ordinary basic standard deduction. Maine follows the federal
    # standard deduction from 2027, so the cap has to reach Maine too.
    simulation = _simulation(
        {
            "person": {
                "age": 17,
                "employment_income": 3_000,
                "is_tax_unit_head": True,
            }
        },
        "SINGLE",
        2027,
        tax_unit_inputs={"head_is_dependent_elsewhere": True},
    )
    maine = simulation.calculate("me_standard_deduction", "2027")[0]
    federal = simulation.calculate("standard_deduction", "2027")[0]
    assert maine == pytest.approx(federal)
    # The cap binds: earned income plus the fixed addition is far below both the
    # federal basic amount and Maine's own frozen amount for a single filer.
    assert maine < _maine_own_amount("SINGLE", 2027)
    assert (
        maine
        < SYSTEM.parameters.gov.irs.deductions.standard.amount("2027-01-01")["SINGLE"]
    )


def test_me_standard_deduction_is_zero_for_a_2027_separate_itemizing_filer():
    # IRC Section 63(c)(6)(A): a married individual filing separately whose
    # spouse itemizes gets no standard deduction. Maine follows the federal
    # standard deduction from 2027, so Maine's is zero as well.
    simulation = _simulation(
        {"person": {"age": 40, "employment_income": 50_000}},
        "SEPARATE",
        2027,
        tax_unit_inputs={"separate_filer_itemizes": True},
    )
    maine = simulation.calculate("me_standard_deduction", "2027")[0]
    federal = simulation.calculate("standard_deduction", "2027")[0]
    assert federal == pytest.approx(0)
    assert maine == pytest.approx(0)
