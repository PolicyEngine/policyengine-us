from policyengine_us.model_api import *


class oh_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Ohio TANF gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    reference = "http://codes.ohio.gov/oac/5101:1-23-20"

    adds = "gov.states.oh.odjfs.tanf.income.earned"
