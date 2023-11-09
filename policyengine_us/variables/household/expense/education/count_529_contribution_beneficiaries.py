from policyengine_us.model_api import *


class count_529_contribution_beneficiaries(Variable):
    value_type = int
    entity = Person
    label = "529 college savings plan beneficiary"
    definition_period = YEAR
