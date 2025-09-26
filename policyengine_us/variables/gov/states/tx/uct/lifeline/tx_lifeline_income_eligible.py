from policyengine_us.model_api import *


class tx_lifeline_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Texas Lifeline income eligible"
    definition_period = YEAR
    defined_for = StateCode.TX
    reference = (
        "https://www.dart.org/fare/general-fares-and-overview/reduced-fares"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.uct.lifeline

        fpg_ratio = spm_unit("fcc_fpg_ratio", period)
        fpg_limit = p.fpg_limit
        return fpg_ratio <= fpg_limit
