from policyengine_us.model_api import *


class s_corp_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "S-Corp self-employment income"
    definition_period = YEAR
    documentation = "Partner self-employment earnings/loss (included in partnership_s_corp_income total)"
    unit = USD
