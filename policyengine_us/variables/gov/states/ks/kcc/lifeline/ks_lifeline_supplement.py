from policyengine_us.model_api import *


class ks_lifeline_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas Lifeline supplement amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.KS
    reference = "https://www.kcc.ks.gov/telecommunications/lifeline"

    adds = ["gov.states.ks.kcc.lifeline.supplement"]
