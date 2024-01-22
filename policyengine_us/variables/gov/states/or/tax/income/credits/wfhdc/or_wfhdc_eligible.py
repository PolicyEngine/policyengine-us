from policyengine_us.model_api import *


class or_wfhdc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Oregon working family household and dependent care credit"
    documentation = "Oregon Working Family Household and Dependent Care Credit household eligibility"
    definition_period = YEAR
    reference = (
        "https://www.oregon.gov/dor/forms/FormsPubs/schedule-or-wfhdc-inst_101-195-1_2022.pdf#pahe=1",
        "https://law.justia.com/codes/oregon/2021/volume-08/chapter-315/section-315-264/",
    )
    defined_for = StateCode.OR

    def formula(tax_unit, period, parameters):
        # Get the parameter tree for the Oregon WFHDC.
        p = parameters(period).gov.states["or"].tax.income.credits.wfhdc

        # Over two individuals have to be present in the tax unit.
        household_size_eligible = (
            tax_unit("tax_unit_size", period) >= p.min_tax_unit_size
        )

        # Get the income threshold based on household size.
        fpg = tax_unit("tax_unit_fpg", period)
        income_threshold = fpg * p.fpg_limit

        # Get household income, the larger of federal and Oregon AGI.
        federal_agi = tax_unit("adjusted_gross_income", period)
        or_agi = tax_unit("or_agi", period)
        household_income = max_(federal_agi, or_agi)

        # Check if household income is below the threshold.
        income_eligible = household_income <= income_threshold

        # Check if the household has a child or disabled member other than the household head.
        # Note that a disabled spouse is a qualifying individual.
        person = tax_unit.members
        age = person("age", period)
        disabled = person("is_disabled", period)
        head = person("is_tax_unit_head", period)
        qualifying_individuals = (age <= p.child_age_limit) | (
            disabled & ~head
        )
        has_qualified_individual = tax_unit.any(qualifying_individuals)

        # employment status
        # 1) you are working
        earned_income = person("earned_income", period)
        earned_income_eligible = tax_unit.any(head * earned_income) > 0
        # 2)  you are single and you attended school (full-time or part-time)
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        attend_school = tax_unit.any(head & person("is_in_school", period))
        # 3) you are married filing jointly and one spouse attended school (full-time) or was disabled
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        is_full_time_student = person("is_full_time_student", period)
        married_eligible = tax_unit.any(
            is_full_time_student & is_head_or_spouse
        )

        employment_eligible = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
                filing_status == status.HEAD_OF_HOUSEHOLD,
            ],
            [
                earned_income_eligible | attend_school,
                earned_income_eligible | married_eligible,
                earned_income_eligible,
                earned_income_eligible,
                earned_income_eligible,
            ],
        )

        # Determine if the household is eligible for the WFHDC.
        return (
            household_size_eligible
            & income_eligible
            & has_qualified_individual
            & employment_eligible
        )
