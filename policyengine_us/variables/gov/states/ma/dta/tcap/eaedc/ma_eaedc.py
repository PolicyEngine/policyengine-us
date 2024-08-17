from policyengine_us.model_api import *


class ma_eaedc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-500#(B)" 
    )

    adds=["ma_eaedc_income_limit"]
    subtracts=["ma_eaedc_net_income"]
    