from policyengine_us.model_api import *


class oh_bonus_depreciation_add_back(Variable):
    value_type = float
    entity = Person
    label = "Ohio bonus depreciation add back"
    definition_period = YEAR
    documentation = ""
    reference = ""
