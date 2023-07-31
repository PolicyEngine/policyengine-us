from policyengine_us.model_api import *


class dc_tanf_gross_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "DC TANF gross earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DC

    adds = "gov.states.dc.dhs.tanf.income.sources.earned"
