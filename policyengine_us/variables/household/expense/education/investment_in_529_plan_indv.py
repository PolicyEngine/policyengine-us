from policyengine_us.model_api import *


class investment_in_529_plan_indv(Variable):
    value_type = float
    entity = Person
    label = "Individual 529 plan investment amounts"
    unit = USD
    documentation = (
        "Amount this person contributed to 529 savings plans during the year, "
        "whoever the beneficiary is. Record a contribution on the person who "
        "made it: a parent's contribution for their child goes on the parent. "
        "State 529 deductions belong to the contributor, so an amount recorded "
        "on a tax unit dependent is the dependent's own and is left off the "
        "head's and spouse's return."
    )
    definition_period = YEAR
