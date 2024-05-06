from policyengine_us.model_api import *


class al_retirement_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Alabama retirement exemption"
    unit = USD
    # Schedule RS Part II & III Line 10
    documentation = "https://www.revenue.alabama.gov/wp-content/uploads/2024/01/23schrsinstr.pdf#page=1"
    definition_period = YEAR
    defined_for = StateCode.AL

    adds = ["al_retirement_exemption_eligible_person"]
