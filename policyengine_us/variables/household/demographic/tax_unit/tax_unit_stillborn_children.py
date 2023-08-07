from policyengine_us.model_api import *


class tax_unit_stillborn_children(Variable):
    value_type = bool
    entity = Person
    label = "Number of stillborn children"
    definition_period = YEAR
