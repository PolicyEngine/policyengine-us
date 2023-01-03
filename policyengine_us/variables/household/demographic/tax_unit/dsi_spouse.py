from policyengine_us.model_api import *


class tax_unit_spouse_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Spouse is tax unit dependent elsewhere"
    documentation = "Whether the spouse of the filer for this tax unit is claimed as a dependent in another tax unit."


dsi_spouse = variable_alias("dsi_spouse", tax_unit_spouse_dependent_elsewhere)
