from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.credits.eitc_helpers import (
    calculate_eitc_like_amount,
)


class co_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado EITC"
    unit = USD
    definition_period = YEAR
    reference = "https://leg.colorado.gov/sites/default/files/te19_colorado_earned_income_tax_credit.pdf"
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        person = tax_unit.members
        age = person("age", period)
        has_tin = person("has_tin", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        filer_has_tin = tax_unit.sum(is_head_or_spouse & ~has_tin) == 0
        federal_identification = person(
            "meets_eitc_identification_requirements", period
        )
        filer_has_federal_identification = (
            tax_unit.sum(is_head_or_spouse & ~federal_identification) == 0
        )
        qualifying_child_with_tin = (
            person("is_qualifying_child_dependent", period) & has_tin
        )
        child_count_with_tin = tax_unit.sum(qualifying_child_with_tin)
        itin_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count_with_tin,
            child_count_with_tin > 0,
            filer_has_tin,
        )

        specified_student = person("is_full_time_college_student", period) | person(
            "is_part_time_college_student", period
        )
        specified_student |= person("technical_institution_student", period)
        homeless_or_foster = person("was_in_foster_care", period) | person.household(
            "is_homeless", period
        )
        under_25_age_eligible = (
            ((age >= 19) & (age < 24) & ~specified_student)
            | (age == 24)
            | ((age >= 18) & (age < 24) & homeless_or_foster)
        )
        under_25_demographic_eligible = tax_unit.any(
            is_head_or_spouse & under_25_age_eligible
        )
        under_25_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            0,
            under_25_demographic_eligible,
            filer_has_federal_identification,
        )
        p = parameters(period).gov.states.co.tax.income.credits
        state_eitc = max_(federal_eitc, max_(itin_eitc, under_25_eitc))
        return state_eitc * p.eitc.match
