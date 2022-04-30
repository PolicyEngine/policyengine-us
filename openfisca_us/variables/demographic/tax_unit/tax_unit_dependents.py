from openfisca_us.model_api import *


class tax_unit_dependents(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Count of tax unit dependents"
    definition_period = YEAR

    formula = sum_of_variables(["is_tax_unit_dependent"])
