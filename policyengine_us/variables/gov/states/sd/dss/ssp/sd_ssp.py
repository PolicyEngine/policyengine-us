from policyengine_us.model_api import *


class sd_ssp(Variable):
    value_type = float
    entity = Person
    label = "South Dakota State Supplemental Payment"
    definition_period = MONTH
    unit = USD
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0501415011DEN"
    adds = ["sd_ssp_independent", "sd_ssp_care"]
