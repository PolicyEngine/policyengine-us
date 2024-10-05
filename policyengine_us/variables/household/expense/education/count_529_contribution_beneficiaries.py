from policyengine_us.model_api import *


class count_529_contribution_beneficiaries(Variable):
    value_type = int
    entity = Person
    label = "Number of beneficiaries to 529 college savings plan contributions"
    definition_period = YEAR
