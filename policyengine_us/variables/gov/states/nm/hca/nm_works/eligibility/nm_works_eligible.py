from policyengine_us.model_api import *


class nm_works_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "New Mexico Works eligible"
    definition_period = MONTH
    reference = "https://www.srca.nm.gov/parts/title08/08.102.0400.html"
    defined_for = StateCode.NM

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        resources_eligible = spm_unit("nm_works_resources_eligible", period)
        gross_income_eligible = spm_unit(
            "nm_works_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("nm_works_net_income_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & resources_eligible
            & gross_income_eligible
            & net_income_eligible
        )
