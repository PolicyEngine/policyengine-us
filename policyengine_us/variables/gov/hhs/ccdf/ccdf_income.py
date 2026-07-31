from policyengine_us.model_api import *


class ccdf_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "CCDF income approximation"
    definition_period = YEAR
    unit = USD
    documentation = (
        "Uses SPM-unit market income as a cross-state approximation. "
        "State CCDF programs may define a different assistance unit and "
        "count different income sources."
    )
    reference = "https://www.law.cornell.edu/uscode/text/42/9858n#4_B"
    adds = ["market_income"]
