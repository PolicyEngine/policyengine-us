from policyengine_us.model_api import *


class count_529_contribution_beneficiaries(Variable):
    value_type = int
    entity = Person
    label = "Number of beneficiaries to 529 college savings plan contributions"
    documentation = (
        "Number of beneficiaries of the 529 plan contributions this person "
        "made during the year (investment_in_529_plan_indv)."
    )
    definition_period = YEAR
