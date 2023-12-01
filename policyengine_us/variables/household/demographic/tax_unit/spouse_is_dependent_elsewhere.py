from policyengine_us.model_api import *


class spouse_is_dependent_elsewhere(Variable):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = "Tax-unit spouse is dependent elsewhere"
    documentation = "Whether the spouse of the filer for this tax unit is claimed as a dependent in another tax unit."
