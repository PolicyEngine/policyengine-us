from policyengine_us.model_api import *


class vt_ccfap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP countable income"
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=9"

    adds = "gov.states.vt.dcf.ccfap.income.sources"
