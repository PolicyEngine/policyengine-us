from policyengine_us.model_api import *


class la_military_compensation(Variable):
    value_type = float
    entity = TaxUnit
    label = "Louisiana military compensation amount"
    defined_for = StateCode.LA
    unit = USD
    definition_period = YEAR