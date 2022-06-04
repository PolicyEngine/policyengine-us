from openfisca_us.model_api import *


class ma_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA income tax"
    unit = USD
    documentation = "Massachusetts State income tax."
    definition_period = YEAR
    is_eligible = in_state("MA")
    reference = "https://www.mass.gov/doc/2021-form-1-massachusetts-resident-income-tax-return/download"

    def formula(tax_unit, period, parameters):
        income_tax_before_credits = tax_unit("ma_income_tax_before_credits", period)
        credits = [
            "ma_limited_income_tax_credit",
            "state_income_tax_refundable_credits",
        ]
        credit_value = add(tax_unit, period, credits)
        return income_tax_before_credits - credit_value