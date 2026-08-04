from policyengine_us.model_api import *


class az_530a_distribution_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = (
        "Arizona Internal Revenue Code section 530A account distribution subtraction"
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ
    reference = (
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://www.azleg.gov/legtext/57leg/2R/bills/HB4168H.pdf#page=28",
    )

    adds = ["az_530a_distribution"]
