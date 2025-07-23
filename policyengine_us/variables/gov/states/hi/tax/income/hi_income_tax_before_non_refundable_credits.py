from policyengine_us.model_api import *


class hi_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii income tax before non-refundable credits"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    # Hawaii Tax Rate Schedules
    reference = "https://tax.hawaii.gov/forms/d_18table-on/d_18table-on_p13/"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        taxable_income = tax_unit("hi_taxable_income", period)
        p = parameters(period).gov.states.hi.tax.income.rates

        income_tax = select_filing_status_value(
            filing_status,
            p,
            taxable_income
        )
        alternative_tax = tax_unit(
            "hi_alternative_tax_on_capital_gains", period
        )

        alternative_tax_eligible = tax_unit(
            "hi_alternative_tax_on_capital_gains_eligible", period
        )
        return where(
            alternative_tax_eligible,
            min_(income_tax, alternative_tax),
            income_tax,
        )
