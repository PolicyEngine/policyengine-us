from policyengine_us.model_api import *


class mn_renters_credit_qualifying_crp(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Has a qualifying Minnesota renter's credit CRP"
    definition_period = YEAR
    default_value = False
    defined_for = StateCode.MN
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/290.0693",
        "https://www.revenue.state.mn.us/crp-instructions",
        "https://www.revenue.state.mn.us/sites/default/files/2026-03/m1rent-25.pdf",
    )
