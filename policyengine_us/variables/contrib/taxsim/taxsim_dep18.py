from policyengine_us.model_api import *


class taxsim_dep18(Variable):
    value_type = float
    entity = TaxUnit
    label = "Children under 13"
    unit = USD
    definition_period = YEAR

    adds = ["is_child_dependent"]
