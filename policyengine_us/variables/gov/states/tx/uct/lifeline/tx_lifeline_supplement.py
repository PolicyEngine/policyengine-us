from policyengine_us.model_api import *


class tx_lifeline_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Lifeline supplement amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    adds = ["gov.states.tx.uct.lifeline.supplement"]
