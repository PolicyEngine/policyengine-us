from policyengine_us.model_api import *


class tax_unit_count_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents"
    definition_period = YEAR

    adds = ["is_tax_unit_dependent"]
