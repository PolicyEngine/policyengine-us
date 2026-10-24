from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.income._apply_medicaid_optional_senior_or_disabled_exclusions import (
    _apply_medicaid_optional_senior_or_disabled_exclusions,
)


class medicaid_optional_senior_or_disabled_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Countable income for Medicaid's optional senior or disabled pathway"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#m",
        "https://www.kff.org/medicaid/medicaid-financial-eligibility-for-seniors-and-people-with-disabilities-findings-from-a-50-state-survey/",
        # Missouri MHABD budgeting order and rounding
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-25/",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-015-00/0805-015-40/",
        # California ABD FPL Part B and health insurance premium deductions
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/20-24.pdf#page=3",
    )

    def formula(person, period, parameters):
        pre_reduction_earned_income = person("ssi_marital_earned_income", period)
        blind_disabled_working_student_income = person(
            "ssi_blind_or_disabled_working_student_exclusion", period
        )
        earned_income = max_(
            pre_reduction_earned_income - blind_disabled_working_student_income,
            0,
        )

        total_unearned_income = add(
            person,
            period,
            [
                "ssi_marital_unearned_income",
                "medicaid_optional_senior_or_disabled_unearned_income_deemed_from_ineligible_parent",
                "ssi_in_kind_support_and_maintenance",
            ],
        )

        couple_computation = person("ssi_couple_computation_applies", period)
        state = person.household("state_code_str", period)
        p = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled.income
        income_disregard = where(
            couple_computation,
            p.disregard.couple[state],
            p.disregard.individual[state],
        )
        personal_countable = _apply_medicaid_optional_senior_or_disabled_exclusions(
            earned_income,
            total_unearned_income,
            state,
            income_disregard,
            parameters,
            period,
        )

        # ACWDL 20-24 deducts Part B "regardless of how the premium is paid",
        # so use the base premium, not the premium net of MSP coverage.
        medicare_enrolled = person("medicare_enrolled", period)
        part_b_premium = person("base_part_b_premium", period) * medicare_enrolled
        other_premiums = person(
            "health_insurance_premiums_without_medicare_part_b", period
        )
        own_premiums = part_b_premium + other_premiums
        premiums = where(
            couple_computation,
            person.marital_unit.sum(own_premiums),
            own_premiums,
        )
        deducts_premiums = p.deducts_health_insurance_premiums[state].astype(bool)
        personal_countable = max_(
            personal_countable - where(deducts_premiums, premiums, 0), 0
        )

        spousal_deemed = person(
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
            period,
        )
        is_eligible_individual = person("is_ssi_eligible_individual", period)
        is_eligible_spouse = person("is_ssi_eligible_spouse", period)
        is_eligible = is_eligible_individual | is_eligible_spouse

        return where(
            ~is_eligible,
            0,
            where(
                couple_computation,
                personal_countable / 2,
                personal_countable + spousal_deemed,
            ),
        )
