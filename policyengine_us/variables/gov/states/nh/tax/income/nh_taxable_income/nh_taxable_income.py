from policyengine_us.model_api import *


class nh_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        dividend_income = tax_unit("nh_dividend_income", period)
        interest_income = tax_unit("nh_interest_income", period)
        return dividend_income + interest_income