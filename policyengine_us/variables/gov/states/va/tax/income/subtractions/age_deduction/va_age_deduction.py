from policyengine_us.model_api import *


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia age deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions.age_deduction

        filing_status = tax_unit("filing_status", period)

        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse

        agi = tax_unit("va_age_deduction_agi", period)

        # Calculate the number of people who are eligible for an age deduction
        head_eligible = age_head >= p.age_minimum
        spouse_eligible = age_spouse >= p.age_minimum
        count_eligible = head_eligible.astype(int) + spouse_eligible.astype(int)

        # Calculate the number of people eligible for a full age deduction
        head_eligible_for_full_deduction = (
            birth_year_head < p.birth_year_limit_for_full_amount
        )
        spouse_eligible_for_full_deduction = (
            birth_year_spouse < p.birth_year_limit_for_full_amount
        )
        count_eligible_for_full_deduction = head_eligible_for_full_deduction.astype(
            int
        ) + spouse_eligible_for_full_deduction.astype(int)

        # Va. Code § 58.1-322.03(5) grants two distinct age deductions:
        # (a) a fixed amount for filers born on or before the birth-year
        # limit, which is *not* income-tested; and (b) an income-based amount
        # for filers born after the limit, reduced dollar-for-dollar by the
        # amount their adjusted federal AGI exceeds the threshold. The income
        # test applies only to the (b) amount, so the fixed (a) amount must be
        # protected from the reduction.
        fixed_count = count_eligible_for_full_deduction
        income_based_count = count_eligible - fixed_count

        fixed_deduction = p.amount * fixed_count
        income_based_maximum = p.amount * income_based_count

        # Calculate the amount that the adjusted federal AGI exceeds the threshold
        excess = max_(agi - p.threshold[filing_status], 0)

        income_based_deduction = max_(income_based_maximum - excess, 0)

        return fixed_deduction + income_based_deduction
