from policyengine_us.model_api import *


class pension_contributions(Variable):
    value_type = float
    entity = Person
    label = "Pension contributions"
    unit = USD
    documentation = "Contributions to IRAs, SEP, and other pension funds."
    definition_period = YEAR

    adds = ["ira_contributions", "sep_simple_qualified_plan_contributions"]
