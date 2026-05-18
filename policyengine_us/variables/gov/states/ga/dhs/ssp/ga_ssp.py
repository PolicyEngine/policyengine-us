from policyengine_us.model_api import *


class ga_ssp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Georgia State Supplementary Payment"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = "https://pamms.dhs.ga.gov/dfcs/medicaid/2578/"

    adds = ["ga_ssp_person"]
