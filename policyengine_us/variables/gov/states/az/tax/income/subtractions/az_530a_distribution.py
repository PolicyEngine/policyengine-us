from policyengine_us.model_api import *


class az_530a_distribution(Variable):
    value_type = float
    entity = Person
    label = "Distribution from an Internal Revenue Code section 530A account"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01022.htm",
        "https://www.azleg.gov/legtext/57leg/2R/bills/HB4168H.pdf#page=28",
    )
