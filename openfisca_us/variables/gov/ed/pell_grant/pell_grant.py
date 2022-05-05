from openfisca_us.model_api import *


class pell_grant(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pell Grant amount"
    documentation = "SPM unit's Pell Grant educational subsidy"
    definition_period = YEAR
    unit = USD
