from openfisca_us.model_api import *


class is_snap_eligible(Variable):
    value_type = float
    entity = SPMUnit
    label = "SNAP eligible"
    unit = "currency-USD"
    documentation = "Whether this SPM unit is eligible for SNAP benefits"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/7/2017#a"
    default_value = True
