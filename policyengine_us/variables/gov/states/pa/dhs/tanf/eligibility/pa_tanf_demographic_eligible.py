from policyengine_us.model_api import *


class pa_tanf_demographic_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF demographic eligibility"
    documentation = "Pennsylvania TANF requires a family to include a minor child (under age 18, or age 18 and full-time student in secondary school) or a pregnant woman with no other children."
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "55 Pa. Code § 153.43, Policy Manual Section 105.2"

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility as baseline
        # Federal rules cover age requirements (under 18 or 18 and in school)
        # and pregnant women eligibility
        return spm_unit("is_demographic_tanf_eligible", period)
