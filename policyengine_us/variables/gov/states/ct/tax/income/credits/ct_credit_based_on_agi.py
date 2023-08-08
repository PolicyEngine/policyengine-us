from policyengine_us.model_api import *


class ct_credit_based_on_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut Credit Based on AGI"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
