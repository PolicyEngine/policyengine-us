from policyengine_us.model_api import *


class mn_renters_credit_seiu_stipend_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit SEIU stipend subtraction"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
