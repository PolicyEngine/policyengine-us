from policyengine_us.model_api import *


class nc_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "North Carolina TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NC

    adds = "gov.states.nc.ncdhhs.tanf.income.earned"
