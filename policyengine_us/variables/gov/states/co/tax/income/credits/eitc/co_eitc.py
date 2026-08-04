from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import (
    calculate_eitc_like_amount,
)


class co_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Colorado EITC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://leg.colorado.gov/sites/default/files/te19_colorado_earned_income_tax_credit.pdf",
        # C.R.S. 39-22-123.5 pays a percentage of the federal IRC 32 credit.
        "https://leg.colorado.gov/sites/default/files/images/olls/crs2023-title-39.pdf",
        # IRC 152(c)(3)(B) waives the qualifying-child age test for permanently and totally disabled individuals.
        "https://www.law.cornell.edu/uscode/text/26/152#c_3_B",
    )
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
        # IRC 152(c)(3)(B) waives the age test for a permanently and totally
        # disabled dependent, matching the federal eitc_child_count.
        is_disabled_dependent = person("is_tax_unit_dependent", period) & person(
            "is_permanently_and_totally_disabled", period
        )
        qualifying_child_with_tin = (
            person("is_qualifying_child_dependent", period) | is_disabled_dependent
        ) & has_tin
        child_count_with_tin = tax_unit.sum(qualifying_child_with_tin)
        federal_eitc_parameters = parameters(period).gov.irs.credits.eitc
        student = person("is_full_time_student", period)
        federal_childless_age_floor = where(
            student,
            federal_eitc_parameters.eligibility.age.min_student,
            federal_eitc_parameters.eligibility.age.min,
        )
        childless_filer_age_eligible = tax_unit.any(
            is_head_or_spouse
            & (age >= federal_childless_age_floor)
            & (age <= federal_eitc_parameters.eligibility.age.max)
        )
        itin_eitc = calculate_eitc_like_amount(
            tax_unit,
            period,
            parameters,
            child_count_with_tin,
            (child_count_with_tin > 0) | childless_filer_age_eligible,
            filer_has_tin,
        )

        specified_student = person("is_full_time_college_student", period) | person(
            "is_part_time_college_student", period
        )
        specified_student |= person("technical_institution_student", period)
        homeless_or_foster = person("was_in_foster_care", period) | person.household(
            "is_homeless", period
        )
        p_u25 = parameters(
            period
        ).gov.states.co.tax.income.credits.eitc.under_25_expansion
        under_25_age_eligible = (
            ((age >= p_u25.min_age) & (age < p_u25.max_age) & ~specified_student)
            | (p_u25.eligible_at_max_age & (age == p_u25.max_age))
            | (
                (age >= p_u25.homeless_or_foster_min_age)
                & (age < p_u25.max_age)
                & homeless_or_foster
            )
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
