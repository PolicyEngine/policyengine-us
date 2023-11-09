from policyengine_us.model_api import *


class college_savigns_plan_529_benefitiary(Variable):
    value_type = int
    entity = Person
    label = "Number of beneficiaries to 529 college savings plan contributions"
    definition_period = YEAR
