from policyengine_us.model_api import *


class ks_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Kansas Temporary Assistance for Families (TANF)"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-70",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-50",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        has_eligible_member = (
            add(spm_unit, period, ["is_person_demographic_tanf_eligible"]) > 0
        )
        income_eligible = spm_unit("ks_tanf_income_eligible", period)
        resources_eligible = spm_unit("ks_tanf_resources_eligible", period)
        return has_eligible_member & income_eligible & resources_eligible
