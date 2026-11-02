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
        # California ABD FPL disregard and Part B and health insurance premium
        # deductions
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/c00-57.pdf#page=3",
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/20-24.pdf#page=3",
        "https://www.dhcs.ca.gov/services/medi-cal/eligibility/letters/Documents/20-18.pdf#page=2",
        "https://www.law.cornell.edu/regulations/california/22-CCR-50555.2",
        "https://www.law.cornell.edu/uscode/text/42/1395r#i",
        "https://www.law.cornell.edu/cfr/text/20/416.1163",
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

        # 22 CCR 50555.2 deducts person-paid premiums, Part B only when the
        # person pays it. From 12/2020 (ACWDL 20-18, 20-24) CA disregards Part B
        # "regardless of how the premium is paid": swap the person-paid Part B
        # in the shared aggregate for the individual's full Part B premium, the
        # base premium plus any IRMAA (42 USC 1395r(i)), whoever pays it.
        # NOTE: medicare_enrolled (Part A and/or Part B) stands in for Part B
        # enrollment, as in medical_expense_health_insurance_premiums.
        # NOTE: gov.hhs.medicare.part_b.base_premium starts in 2021, so a
        # person-paid Part B before 2021 reads the 2021 premium.
        # NOTE: ACWDL 20-24 Example 5 also deducts a non-applicant spouse's
        # premiums. Spousal income here follows SSI deeming (20 CFR 416.1163),
        # so that premium is not modeled, nor is MC 176's maintenance need
        # deduction for the spouse (lines 19 and 21; issue 10543).
        medicare_enrolled = person("medicare_enrolled", period)
        paid_premiums = person("medical_expense_health_insurance_premiums", period)
        paid_part_b = person("medicare_part_b_premium", period) * medicare_enrolled
        full_part_b = (
            person("gross_medicare_part_b_premium", period) * medicare_enrolled
        )
        disregards_part_b = p.disregards_medicare_part_b_premium[state].astype(bool)
        own_premiums = where(
            disregards_part_b,
            max_(paid_premiums - paid_part_b, 0) + full_part_b,
            paid_premiums,
        )
        premiums = where(
            couple_computation,
            person.marital_unit.sum(own_premiums),
            own_premiums,
        )
        deducts_premiums = p.deducts_health_insurance_premiums[state].astype(bool)
        # MC 176 (ACWDL 00-57) lines 16-17 subtract the additional disregard
        # and the premiums from income after the SSI exclusions.
        additional_disregard = (
            where(
                couple_computation,
                p.additional_disregard.couple[state],
                p.additional_disregard.individual[state],
            )
            * MONTHS_IN_YEAR
        )
        deductions = where(deducts_premiums, premiums, 0) + additional_disregard

        spousal_deemed = person(
            "medicaid_optional_senior_or_disabled_income_deemed_from_ineligible_spouse",
            period,
        )
        is_eligible_individual = person("is_ssi_eligible_individual", period)
        is_eligible_spouse = person("is_ssi_eligible_spouse", period)
        is_eligible = is_eligible_individual | is_eligible_spouse

        # ACWDL 20-24 Examples 2 and 5 combine the non-applicant spouse's
        # income with the applicant's income before the deductions, as
        # 20 CFR 416.1163(d)(2) does, so subtract the deductions from the
        # combined income and floor the result.
        countable = where(
            couple_computation,
            max_(personal_countable - deductions, 0) / 2,
            max_(personal_countable + spousal_deemed - deductions, 0),
        )
        return where(is_eligible, countable, 0)
