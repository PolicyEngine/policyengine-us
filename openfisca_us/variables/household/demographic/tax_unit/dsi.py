from openfisca_us.model_api import *


class tax_unit_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Is tax unit dependent elsewhere"
    documentation = "Whether the filer for this tax unit is claimed as a dependent in another tax unit."


dsi = variable_alias("dsi", tax_unit_dependent_elsewhere)
