"""The historical child AMT fixes leave post-2017 AMT unchanged.

Compare the model to both formulas as they stood before these fixes, rather
than assuming that equal AMTI and regular taxable income conceal a change.
Section 55(d)(4)(A)(iii) disapplies section 59(j) from 2018 onward.
"""

from itertools import product

import hypothesis
import numpy as np
import pytest
from hypothesis import strategies as st

from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable
from policyengine_us import Simulation
from policyengine_us.system import system

STATUSES = (
    "SINGLE",
    "JOINT",
    "SEPARATE",
    "HEAD_OF_HOUSEHOLD",
    "SURVIVING_SPOUSE",
)
OUTPUTS = (
    "amt_exemption",
    "amt_income_less_exemptions",
    "amt_base_tax",
    "alternative_minimum_tax",
)
YEARS = tuple(range(2018, 2031))


class PreviousChildAmtFormulas(Reform):
    """Restore the two formulas from main before the historical fixes."""

    def apply(self):
        class amt_kiddie_tax_applies(Variable):
            def formula(tax_unit, period, parameters):
                p = parameters(period).gov.irs.dependent.ineligible_age
                person = tax_unit.members
                is_student = person("is_full_time_student", period)
                head_is_student = tax_unit.any(
                    is_student & person("is_tax_unit_head", period)
                )
                spouse_is_student = tax_unit.any(
                    is_student & person("is_tax_unit_spouse", period)
                )
                age_head = tax_unit("age_head", period)
                age_spouse = tax_unit("age_spouse", period)
                head_age_limit = np.where(head_is_student, p.student, p.non_student)
                spouse_age_limit = np.where(spouse_is_student, p.student, p.non_student)
                young_head = (age_head != 0) & (age_head < head_age_limit)
                no_or_young_spouse = (age_spouse == 0) | (age_spouse < spouse_age_limit)
                return young_head & no_or_young_spouse

        class amt_income_less_exemptions(Variable):
            def formula(tax_unit, period, parameters):
                p = parameters(period).gov.irs.income.amt
                amt_income = tax_unit("amt_income", period)
                if p.exemption.child.in_effect:
                    applied_income = np.where(
                        tax_unit("amt_kiddie_tax_applies", period),
                        tax_unit("taxable_income", period),
                        amt_income,
                    )
                else:
                    applied_income = amt_income
                return np.maximum(0, applied_income - tax_unit("amt_exemption", period))

        self.update_variable(amt_kiddie_tax_applies)
        self.update_variable(amt_income_less_exemptions)


@pytest.fixture(scope="module")
def previous_system():
    return PreviousChildAmtFormulas(system)


def boundary_cases(year):
    """Include every status, age branch, phaseout stage, and tax comparison."""
    p = system.parameters(str(year)).gov.irs.income.amt.exemption
    for status, (age, student) in product(
        STATUSES, ((17, False), (18, False), (22, True), (40, False))
    ):
        exemption = p.amount[status]
        phaseout_start = p.phase_out.start[status]
        incomes = (
            0,
            50_000,
            exemption + 100_000,
            phaseout_start,
            phaseout_start + exemption / (2 * p.phase_out.rate),
            phaseout_start + exemption / p.phase_out.rate + 1,
        )
        for income, regular_tax_fraction in product(incomes, (0, 0.2, 1)):
            yield {
                "status": status,
                "age": age,
                "student": student,
                "amt_income": income,
                "deductions": 25_000,
                "regular_tax": income * regular_tax_fraction,
            }


def situation(cases, year):
    people, tax_units, households = {}, {}, {}
    for i, case in enumerate(cases):
        joint = case["status"] == "JOINT"
        members = [f"head_{i}"]
        for role in ("head", "spouse") if joint else ("head",):
            person_id = f"{role}_{i}"
            people[person_id] = {
                "age": {year: case["age"]},
                "is_full_time_student": {year: case["student"]},
                "is_tax_unit_head": {year: role == "head"},
                "is_tax_unit_spouse": {year: role == "spouse"},
                "is_tax_unit_dependent": {year: False},
            }
            if role == "spouse":
                members.append(person_id)
        tax_units[f"unit_{i}"] = {
            "members": members,
            "filing_status": {year: case["status"]},
            "age_head": {year: case["age"]},
            "age_spouse": {year: case["age"] if joint else 0},
            "amt_income": {year: case["amt_income"]},
            "taxable_income": {year: max(0, case["amt_income"] - case["deductions"])},
            "regular_tax_before_credits": {year: case["regular_tax"]},
            "amt_part_iii_required": {year: False},
            "amt_tax_including_cg": {year: 0},
            "foreign_earned_income_exclusion": {year: 0},
            "foreign_tax_credit_potential": {year: 0},
            "form_4972_lumpsum_distributions": {year: 0},
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": {year: "TX"},
        }
    return {"people": people, "tax_units": tax_units, "households": households}


def multi_year_situation(extra_cases):
    """Merge annual inputs while keeping each cohort's membership fixed."""
    inputs = {"people": {}, "tax_units": {}, "households": {}}
    for year_index, year in enumerate(YEARS):
        cases = [
            *boundary_cases(year),
            *(
                {
                    "status": case["status"],
                    "age": case["age"],
                    "student": case["student"],
                    **case["finances"][year_index],
                }
                for case in extra_cases
            ),
        ]
        for entity_type, entities in situation(cases, year).items():
            for entity_id, fields in entities.items():
                merged = inputs[entity_type].setdefault(entity_id, {})
                for variable, value in fields.items():
                    if variable == "members":
                        assert merged.setdefault(variable, value) == value
                    else:
                        merged.setdefault(variable, {}).update(value)
    return inputs


financial_strategy = st.fixed_dictionaries(
    {
        "amt_income": st.integers(0, 3_000_000),
        "deductions": st.integers(0, 100_000),
        "regular_tax": st.integers(0, 1_000_000),
    }
)
case_strategy = st.fixed_dictionaries(
    {
        "status": st.sampled_from(STATUSES),
        "age": st.integers(17, 40),
        "student": st.booleans(),
        "finances": st.lists(
            financial_strategy, min_size=len(YEARS), max_size=len(YEARS)
        ),
    }
)


@hypothesis.settings(max_examples=3, deadline=None, derandomize=True)
@hypothesis.given(
    extra_cases=st.lists(case_strategy, min_size=1, max_size=4),
)
def test_post_2017_amt_is_unchanged(previous_system, extra_cases):
    inputs = multi_year_situation(extra_cases)
    current = Simulation(tax_benefit_system=system, situation=inputs)
    previous = Simulation(tax_benefit_system=previous_system, situation=inputs)

    for year in YEARS:
        for variable in OUTPUTS:
            np.testing.assert_array_equal(
                current.calculate(variable, year),
                previous.calculate(variable, year),
                err_msg=f"{variable} changed in {year}",
            )

        # Confirm the joint-return fix actually changes eligibility in this
        # vector, while the statutory switch keeps post-2017 AMT identical.
        eligibility_changed = current.calculate(
            "amt_kiddie_tax_applies", year
        ) != previous.calculate("amt_kiddie_tax_applies", year)
        assert eligibility_changed.any()
        filing_status = current.calculate("filing_status", year)
        assert np.all(filing_status.decode_to_str()[eligibility_changed] == "JOINT")

        exemption = current.calculate("amt_exemption", year)
        base_exemption = system.parameters(
            str(year)
        ).gov.irs.income.amt.exemption.amount[filing_status]
        assert np.any(exemption == base_exemption)
        assert np.any((exemption > 0) & (exemption < base_exemption))
        assert np.any(exemption == 0)
        amt = current.calculate("alternative_minimum_tax", year)
        assert np.any(amt == 0)
        assert np.any(amt > 0)
