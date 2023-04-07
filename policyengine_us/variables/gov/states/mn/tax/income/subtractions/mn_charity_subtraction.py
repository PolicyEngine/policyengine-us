from policyengine_us.model_api import *


class mn_charity_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota charity subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.taxformfinder.org/forms/2021/2021-minnesota-form-m1m.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1m_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        charity = tax_unit("charitable_deduction", period)
        itemizing = tax_unit("mn_itemizing", period)
        p = parameters(period).gov.states.mn.tax.income.subtractions.charity
        subtraction_amount = p.fraction * max_(0, charity - p.threshold)
        return where(itemizing, 0, subtraction_amount)
