from policyengine_us.model_api import *


class tax_unit_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents in the tax unit"
    definition_period = YEAR

    adds = ["is_tax_unit_dependent"]
