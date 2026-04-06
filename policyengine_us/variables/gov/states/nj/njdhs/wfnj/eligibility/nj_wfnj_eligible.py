from policyengine_us.model_api import *


class nj_wfnj_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Jersey WFNJ eligible"
    definition_period = MONTH
    defined_for = StateCode.NJ
    reference = (
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-1",
        "https://www.law.cornell.edu/regulations/new-jersey/N-J-A-C-10-90-3-20",
    )

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("nj_wfnj_income_eligible", period)
        resources_eligible = spm_unit("nj_wfnj_resources_eligible", period)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        has_citizen_or_legal_immigrant = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        return (
            income_eligible
            & resources_eligible
            & demographic_eligible
            & has_citizen_or_legal_immigrant
        )
