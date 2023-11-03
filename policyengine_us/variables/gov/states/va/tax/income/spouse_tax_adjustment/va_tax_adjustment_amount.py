from policyengine_us.model_api import *


class va_tax_adjsutment_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        person = tax_unit.members
        personal_va_agi = person("va_agi", period)
        total_personal_exemptions = (
            personal_exemption_age_qualification
            + personal_exemption_blind_qualification
        ) * p.age_blind_multiplier + p.addition_amount

        eligibility_requirement = personal_va_agi - total_personal_exemptions

        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse

        min_eligibility_value = tax_unit.min_(
            head_or_spouse * eligibility_requirement
        )
        temp_value = max_(va_taxable_income - min_eligibility_value, 0)
        half_of_taxable_income = va_taxable_income / p.divider
        min_temp = min_(min_eligibility_value, half_of_taxable_income)
        max_temp = max_(temp_value, half_of_taxable_income)
        sum_amount = min_temp + max_temp
        tax_amount = va_income_tax
        tax_adjustment_amount = min_(
            where(
                min_eligibility_value > p.threshold
                and va_taxable_income > p.taxable_income_threshold,
                p.adjustment_limit,
                tax_amount - sum_amount,
            ),
            p.adjustment_limit,
        )
