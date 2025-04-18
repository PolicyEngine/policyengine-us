from policyengine_us.model_api import *


class nh_income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire income tax before refundable credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        income = max_(0, tax_unit("nh_taxable_income", period))
        p = parameters(period).gov.states.nh.tax.income
        return income * p.rate * p.in_effect
