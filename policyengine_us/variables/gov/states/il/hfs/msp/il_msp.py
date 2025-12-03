from policyengine_us.model_api import *


class il_msp(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Illinois Medicare Savings Program benefit"
    definition_period = MONTH
    documentation = (
        "Illinois Medicare Savings Program (MSP) benefit. "
        "Illinois uses the federal MSP rules without modifications."
    )
    reference = (
        "https://hfs.illinois.gov/medicalprograms/msp.html",
        "https://www.cms.gov/medicare/costs/medicare-savings-programs",
    )
    defined_for = StateCode.IL
    adds = ["msp"]
