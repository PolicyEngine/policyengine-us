from policyengine_us.model_api import *


class spm_work_childcare_earnings(Variable):
    value_type = float
    entity = Person
    label = "earnings relevant to Census SPM work and childcare expense caps"
    definition_period = YEAR
    unit = USD

    adds = [
        "employment_income",
        "self_employment_income",
        "sstb_self_employment_income",
        "farm_operations_income",
    ]
