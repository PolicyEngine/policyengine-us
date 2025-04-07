from policyengine_us.model_api import *


class mn_income_tax_before_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota income tax before credits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        basic_tax = tax_unit("mn_basic_tax", period)
        amt = tax_unit("mn_amt", period)
        # Only add NIIT if it's in effect
        if parameters(period).gov.states.mn.tax.income.niit.in_effect:
            niit = tax_unit("mn_niit", period)
            return basic_tax + amt + niit
        return basic_tax + amt
