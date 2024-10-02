from policyengine_us.model_api import *


class tax_unit_child_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of child dependents in the tax unit"
    definition_period = YEAR

    adds = ["is_child_dependent"]
