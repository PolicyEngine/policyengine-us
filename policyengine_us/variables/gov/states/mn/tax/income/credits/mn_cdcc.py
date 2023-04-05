from policyengine_us.model_api import *


class mn_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota child and dependent care expenses credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-02/m1cd_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1cd_22_0.pdf"
    )
    defined_for = StateCode.MN

    # def formula(tax_unit, period, parameters):
    #    p = parameters(period).gov.states.mn.tax.income.credits
    #    return p.cdcc_fraction * tax_unit("cdcc", period)
