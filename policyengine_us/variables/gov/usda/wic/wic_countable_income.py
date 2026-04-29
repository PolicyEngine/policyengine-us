from policyengine_us.model_api import *


class wic_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "WIC countable income"
    documentation = "SPM unit income counted for WIC direct income eligibility"
    reference = "https://www.law.cornell.edu/cfr/text/7/246.7#d_2_ii"

    adds = "gov.usda.wic.income.sources"
