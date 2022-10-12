from policyengine_us.model_api import *


class tax_unit_count_dependents(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of dependents"
    definition_period = YEAR

    formula = sum_of_variables(["is_tax_unit_dependent"])
