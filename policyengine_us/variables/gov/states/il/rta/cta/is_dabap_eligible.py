from policyengine_us.model_api import *


class il_dabap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for the Illinois Department on Aging's Benefit Access Program"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://www.transitchicago.com/reduced-fare-programs/#rtareduced"
    )
