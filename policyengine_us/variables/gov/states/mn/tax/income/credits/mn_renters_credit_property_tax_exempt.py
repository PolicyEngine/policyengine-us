from policyengine_us.model_api import *


class mn_renters_credit_property_tax_exempt(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota renter's credit property is exempt from property tax"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
