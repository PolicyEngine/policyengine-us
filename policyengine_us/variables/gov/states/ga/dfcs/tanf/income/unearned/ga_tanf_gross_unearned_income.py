from policyengine_us.model_api import *


class ga_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia TANF gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://pamms.dhs.ga.gov/dfcs/tanf/1525/",
        "https://pamms.dhs.ga.gov/dfcs/tanf/1530/",
    )
    defined_for = StateCode.GA

    adds = [
        "social_security",
        # Note: SSI is excluded from TANF unearned income
        "unemployment_compensation",
        "child_support_received",
        "alimony_income",
    ]
