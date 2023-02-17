from policyengine_us.model_api import *


class me_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ME
