from policyengine_us.model_api import *


class takes_up_ak_permanent_fund_dividend_if_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Takes up the Alaska Permanent Fund Dividend if eligible"
    documentation = (
        "Whether Alaska pays this person the Permanent Fund Dividend and any "
        "energy relief when they pass ak_permanent_fund_dividend_eligible. Set "
        "this to false for someone who did not apply or who fails a test "
        "PolicyEngine cannot resolve from its inputs, such as residence during all "
        "of the prior calendar year or a child's birth during the dividend "
        "year. It defaults to true, so a household calculation pays every "
        "eligible Alaska resident unless an input says otherwise. "
        "See docs/validation/alaska-pfd.md."
    )
    definition_period = YEAR
    default_value = True
