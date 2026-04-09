from policyengine_us.model_api import *


class mn_renters_credit_shared_rent_fraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Claimant share of Minnesota renter's credit CRP rent"
    unit = "/1"
    definition_period = YEAR
    default_value = 1
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf"
    )
