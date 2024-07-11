from policyengine_us.model_api import *


class tax_unit_grandparents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of grandparents in the tax unit"
    definition_period = YEAR

    adds = ["is_grandparent_of_filer_or_spouse"]
