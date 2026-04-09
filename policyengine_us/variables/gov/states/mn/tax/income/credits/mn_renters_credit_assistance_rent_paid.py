from policyengine_us.model_api import *


class mn_renters_credit_assistance_rent_paid(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota renter's credit assistance-paid rent amount"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf"
    )
