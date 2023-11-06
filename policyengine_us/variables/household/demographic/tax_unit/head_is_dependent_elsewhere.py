from policyengine_us.model_api import *


class head_is_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Is tax-unit head a dependent elsewhere"
    documentation = "Whether the filer for this tax unit is claimed as a dependent in another tax unit."
