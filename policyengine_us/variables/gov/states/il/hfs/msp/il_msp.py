from policyengine_us.model_api import *


class il_msp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Illinois Medicare Savings Program benefit"
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/medicaresavings.html",
    )
    defined_for = StateCode.IL

    adds = ["msp"]
