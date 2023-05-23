from policyengine_us.model_api import *


class nh_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        income = tax_unit("nh_taxable_income", period)
        rate = parameters(period).gov.states.nh.tax.income.main
        return income * rate
