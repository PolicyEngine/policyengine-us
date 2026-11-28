from policyengine_us.model_api import *


class ak_hap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Eligible for the Alaska Heating Assistance Program"
    reference = (
        "http://dpaweb.hss.state.ak.us/manuals/HAP/3004/3004-5_grant_computation.htm",
        "https://www.akleg.gov/basis/aac.asp?media=print&secStart=7.44.010&secEnd=7.44.9001",
    )
    defined_for = StateCode.AK

    def formula(spm_unit, period, parameters):
        # The award applies every eligibility condition of 7 AAC 44, including
        # the 2.0-point minimum of 44.080(m), which is tested after the
        # dwelling share (h) and the utility-allowance reduction (l). So a
        # household is eligible exactly when it has an award.
        return spm_unit("ak_hap", period) > 0
