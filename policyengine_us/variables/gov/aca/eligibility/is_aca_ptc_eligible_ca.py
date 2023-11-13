from policyengine_us.model_api import *


class is_aca_ptc_eligible_ca(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for ACA PTC in California"
    definition_period = YEAR
    defined_for = StateCode.CA
    adds = ["is_aca_ptc_eligible"]
