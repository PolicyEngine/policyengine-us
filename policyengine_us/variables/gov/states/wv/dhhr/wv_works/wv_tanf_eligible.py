from policyengine_us.model_api import *


class wv_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for West Virginia WV Works"
    definition_period = MONTH
    reference = (
        "https://dhhr.wv.gov/bcf/Services/familyassistance/Pages/WV-WORKS.aspx"
    )
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("wv_tanf_income_eligible", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        return income_eligible & demographic_eligible
