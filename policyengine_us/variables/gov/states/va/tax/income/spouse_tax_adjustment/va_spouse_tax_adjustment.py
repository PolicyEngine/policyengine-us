from policyengine_us.model_api import *


class va_spouse_tax_adjsutment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia Spouse Tax Adjustment"
    defined_for = "va_spouse_tax_adjsutment_eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=19"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.spouse_head_adjustment
        p1 = parameters(period).gov.states.va.tax.income
        exemptions = person("va_agi_less_exemptions_indv", period)
        smaller_exemption = tax_unit.min(exemptions)
        va_taxable_income = tax_unit("va_taxable_income", period)
        taxable_income_less_exemption = max_(
            va_taxable_income - smaller_exemption, 0
        )

        half_of_taxable_income = va_taxable_income / p.divider
        smaller_temp = p1.rates * min_(
            smaller_exemption, half_of_taxable_income
        )
        larger_temp = p1.rates * max_(
            taxable_income_less_exemption, half_of_taxable_income
        )
        sum_temp = smaller_temp + larger_temp

        tax_amount = tax_unit("va_income_tax", period)

        adjustment_limit_condition = (
            smaller_exemption
            > p.threshold & tax_unit("va_taxable_income", period)
            > p.taxable_income_threshold
        )

        adjustment_amount = tax_amount - sum_amount

        tax_adjustment_amount = tax_unit(
            "va_spouse_adjustment_qualification", period
        ) * min_(
            where(
                adjustment_limit_condition,
                p.adjustment_limit,
                adjustment_amount,
            ),
            p.adjustment_limit,
        )
        return tax_adjustment_amount
