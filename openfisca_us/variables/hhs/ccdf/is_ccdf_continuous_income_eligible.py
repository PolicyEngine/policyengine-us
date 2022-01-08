from openfisca_us.model_api import *


class is_ccdf_continuous_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Continuous income eligibility for CCDF"
