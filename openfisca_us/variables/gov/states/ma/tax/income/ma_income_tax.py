from openfisca_us.model_api import *


class ma_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax"
    unit = USD
    documentation = "Massachusetts State income tax."
    definition_period = YEAR
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"

    def formula(tax_unit, period, parameters):
        in_ma = tax_unit.household("state_code_str", period) == "MA"
        income_tax_before_credits = tax_unit(
            "ma_income_tax_before_credits", period
        )
        p = parameters(period).gov.states.ma.tax.income
        credit_value = add(tax_unit, period, p.credits.allowed)
        return in_ma * (income_tax_before_credits - credit_value)
