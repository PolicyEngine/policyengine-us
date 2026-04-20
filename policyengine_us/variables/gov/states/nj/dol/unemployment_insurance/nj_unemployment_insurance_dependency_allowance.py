from policyengine_us.model_api import *


class nj_unemployment_insurance_dependency_allowance(Variable):
    value_type = float
    entity = Person
    label = "New Jersey unemployment insurance dependency allowance rate"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.nj.gov/labor/myunemployment/before/about/howtoapply/dependencybenefits.shtml",
        "https://www.nj.gov/labor/ea/help/employer_handbook/ui.shtml",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        year = period.this_year
        p = parameters(period).gov.states.nj.dol.unemployment_insurance
        age = person("age", year)
        earnings = add(
            person, period, ["employment_income", "self_employment_income"]
        )
        filing_status = person.tax_unit("filing_status", year)
        head_or_spouse = person("is_tax_unit_head", year) | person(
            "is_tax_unit_spouse", year
        )
        spouse_present = filing_status == filing_status.possible_values.JOINT
        spouse_earnings = person.tax_unit.sum(head_or_spouse * earnings) - (
            head_or_spouse * earnings
        )
        spouse_employed = spouse_present & (spouse_earnings > 0)
        # Tax-unit dependency status is our closest proxy for the qualifying-child relationship.
        qualifying_children = (
            person("is_tax_unit_dependent", year)
            & (earnings <= 0)
            & (
                (age < 19)
                | ((age < 22) & person("is_full_time_student", year))
                | person("is_disabled", year)
            )
        )
        capped_dependents = min_(
            person.tax_unit.sum(qualifying_children)
            + where(spouse_present & ~spouse_employed, 1, 0),
            p.max_dependents,
        )
        calculated_rate = where(
            capped_dependents > 0,
            p.dependency_allowance_first
            + max_(0, capped_dependents - 1)
            * p.dependency_allowance_additional,
            0,
        )
        return where(
            spouse_employed,
            0,
            min_(calculated_rate, p.max_dependency_allowance),
        )
