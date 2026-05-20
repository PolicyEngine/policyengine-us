from policyengine_us.model_api import *


class ssi_receives_food_from_others(Variable):
    value_type = bool
    entity = Person
    label = "Receives food from others for SSI ISM purposes"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/20/416.1130",
        "https://www.federalregister.gov/documents/2024/03/27/2024-06464/omitting-food-from-in-kind-support-and-maintenance-calculations",
    )
