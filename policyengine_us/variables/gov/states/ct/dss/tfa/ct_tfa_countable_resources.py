from policyengine_us.model_api import *


class ct_tfa_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut Temporary Family Assistance (TFA) countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
