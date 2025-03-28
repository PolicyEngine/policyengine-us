from policyengine_us.model_api import *


class ma_eaedc(Variable):
    value_type = float
    entity = SPMUnit
    label = "Massachusetts EAEDC"
    unit = USD
    definition_period = MONTH
    defined_for = "ma_eaedc_eligible"
    reference = "https://www.law.cornell.edu/regulations/massachusetts/department-106-CMR/title-106-CMR-701.000"

    # Program value can not be less than 0
    # due to the eligibility requirements
    adds = ["ma_eaedc_standard_assistance"]
    subtracts = ["ma_eaedc_net_income"]
