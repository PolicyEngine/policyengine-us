from policyengine_us.model_api import *


class ga_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = (
        "Eligible for Georgia Temporary Assistance for Needy Families (TANF)"
    )
    definition_period = MONTH
    reference = (
        "https://rules.sos.ga.gov/gac/290-2-28",
        "https://dfcs.georgia.gov/services/temporary-assistance-needy-families/tanf-eligibility-requirements",
        "https://pamms.dhs.ga.gov/dfcs/tanf/",
    )
    defined_for = StateCode.GA

    def formula(spm_unit, period, parameters):
        income_eligible = spm_unit("ga_tanf_income_eligible", period)
        resources_eligible = spm_unit("ga_tanf_resources_eligible", period)
        return income_eligible & resources_eligible
