from policyengine_us.model_api import *


class ak_energy_relief(Variable):
    value_type = float
    entity = Person
    label = "Alaska One Time Energy Relief"
    unit = USD
    definition_period = YEAR
    reference = "https://pfd.alaska.gov"
    defined_for = StateCode.AK

    adds = ["gov.states.ak.dor.energy_relief"]
