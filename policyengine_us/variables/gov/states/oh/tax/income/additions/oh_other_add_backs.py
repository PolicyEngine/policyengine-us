from policyengine_us.model_api import *


class oh_other_add_backs(Variable):
    value_type = float
    entity = Person
    label = "Ohio other add backs"
    definition_period = YEAR
    defined_for = StateCode.OH
    documentation = ""
    reference = ""
