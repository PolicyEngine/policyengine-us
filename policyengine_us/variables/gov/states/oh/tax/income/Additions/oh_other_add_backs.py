from policyengine_us.model_api import *


class oh_other_add_backs(Variable):
    value_type = float
    entity = TaxUnit
    label = "OH other add backs"
    definition_period = YEAR
    documentation = ""
    reference = ""
