from policyengine_us.model_api import *


class mn_renters_credit_separate_lived_apart_all_year(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Minnesota renter's credit married filing separately lived apart all year"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MN
    reference = (
        "https://www.revenue.state.mn.us/renters-credit-faqs",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
