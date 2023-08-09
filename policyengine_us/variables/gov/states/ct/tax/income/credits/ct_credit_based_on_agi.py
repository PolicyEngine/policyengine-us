from policyengine_us.model_api import *


class ct_personal_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Personal Credits"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
