from policyengine_us.model_api import *


class mn_lumpsum_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota lump-sum tax"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1ls_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1ls_22.pdf"
    )
    defined_for = StateCode.MN

    # def formula(tax_unit, period, parameters):
