from policyengine_us.model_api import *


class pension_contributions(Variable):
    value_type = float
    entity = Person
    label = "Pension contributions"
    unit = USD
    documentation = "Contributions to IRAs, SEP, and other pension funds."
    definition_period = YEAR

    formula = sum_of_variables(
        ["ira_contributions", "sep_simple_qualified_plan_contributions"]
    )
