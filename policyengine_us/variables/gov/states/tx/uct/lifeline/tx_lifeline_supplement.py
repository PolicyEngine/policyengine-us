from policyengine_us.model_api import *


class tx_lifeline_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Lifeline supplement amount"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.TX
    reference = "https://www.law.cornell.edu/regulations/texas/16-Tex-Admin-Code-SS-26-412"

    adds = ["gov.states.tx.uct.lifeline.supplement"]
