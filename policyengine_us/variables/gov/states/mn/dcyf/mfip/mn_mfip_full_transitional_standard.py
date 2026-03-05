from policyengine_us.model_api import *


class mn_mfip_full_transitional_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Minnesota MFIP full Transitional Standard (cash + food)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.revisor.mn.gov/statutes/cite/142G.17#stat.142G.17.5"
    )
    defined_for = StateCode.MN
    adds = ["mn_mfip_cash_portion", "mn_mfip_food_portion"]
