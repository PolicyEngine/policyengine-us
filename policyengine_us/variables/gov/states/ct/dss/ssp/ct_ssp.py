from policyengine_us.model_api import *


class ct_ssp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut State Supplement to the Aged, Blind or Disabled"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CT
    reference = "https://www.cga.ct.gov/current/pub/chap_319s.htm#sec_17b-600"

    adds = ["ct_ssp_person"]
