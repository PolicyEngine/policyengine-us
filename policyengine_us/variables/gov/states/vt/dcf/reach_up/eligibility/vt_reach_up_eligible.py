from policyengine_us.model_api import *


class vt_reach_up_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Vermont Reach Up eligible"
    definition_period = MONTH
    reference = (
        "https://legislature.vermont.gov/statutes/fullchapter/33/011",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # NOTE: Act 133 (2021 Adj. Sess.) extended dependent child age from 19 to 22
        # for full-time students, effective Jan 1, 2024. Not modeled.
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        income_eligible = spm_unit("vt_reach_up_income_eligible", period)
        resources_eligible = spm_unit("vt_reach_up_resources_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resources_eligible
        )
