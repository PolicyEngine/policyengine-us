from policyengine_us.model_api import *


class mt_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) gross unearned income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT

    adds = ["mt_tanf_gross_unearned_income_person"]
