from policyengine_us.model_api import *


class va_tax_adjsutment_calculation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia aged/blind exemption"
    defined_for = StateCode.VA
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p1 = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        p = parameters(period).gov.states.va_tax.income
        min_amount = min(
            va_agi_head - va_personal_exemption_head,
            va_agi_spouse - va_personal_exemption_spouse,
        )

        half_of_taxable_income = va_taxable_income / p1.divider
        diff_amount = min_amount - va_taxable_income
        tax_min = min_(min_amount, half_of_taxable_income) * p.rates
        tax_max = max(diff_amount, half_of_taxable_income) * p.rates
        tax_sum = tax_min + tax_max
        return where(
            min_amount > p.threshold
            and va_taxable_income > p.taxable_threshold,
            p1.adjustment_limit,
            round(va_taxable_income * p.rates) - tax_sum
        )
