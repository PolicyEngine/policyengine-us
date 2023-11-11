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

        min_eligibility_value = tax_unit.min_(
            person("is_tax_unit_head_or_spouse", period)
            * eligibility_requirement
        )
        va_taxable_income = tax_unit("va_taxable_income", period)

        temp_value = max_(va_taxable_income - min_eligibility_value, 0)
        half_of_taxable_income = va_taxable_income / p.divider
        min_temp = p1.rates * min_(
            min_eligibility_value, half_of_taxable_income
        )
        max_temp = p1.rates * max_(temp_value, half_of_taxable_income)
        sum_amount = min_temp + max_temp

        tax_amount = tax_unit("va_income_tax", period)

        adjustment_limit_condition = (
            min_eligibility_value
            > p.threshold & tax_unit("va_taxable_income", period)
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