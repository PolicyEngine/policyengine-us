from policyengine_us.model_api import *


class nh_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New Hampshire Child Care Scholarship Program countable income"
    definition_period = MONTH
    unit = USD
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.06"

    adds = "gov.states.nh.dhhs.ccap.income.countable_income.sources"
