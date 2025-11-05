from policyengine_us.model_api import *


class ga_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF gross earned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/1530/",
    )
    defined_for = StateCode.GA

    adds = ["employment_income", "self_employment_income"]
