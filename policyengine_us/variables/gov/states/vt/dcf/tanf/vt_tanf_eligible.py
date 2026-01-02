from policyengine_us.model_api import *


class vt_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Vermont TANF eligible"
    definition_period = MONTH
    reference = (
        "https://legislature.vermont.gov/statutes/fullchapter/33/011",
        "https://www.law.cornell.edu/regulations/vermont/13-220-Code-Vt-R-13-170-220-X",
    )
    defined_for = StateCode.VT

    def formula(spm_unit, period, parameters):
        # Federal demographic eligibility
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Federal immigration eligibility (any member qualifies)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        # State income eligibility
        income_eligible = spm_unit("vt_tanf_income_eligible", period)
        # State resource eligibility
        resource_eligible = spm_unit("vt_tanf_resource_eligible", period)
        return (
            demographic_eligible
            & immigration_eligible
            & income_eligible
            & resource_eligible
        )
