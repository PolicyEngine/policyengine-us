from policyengine_us.model_api import *


class nv_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Nevada TANF eligible"
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ/"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Use federal demographic eligibility (minor child with deprived parent)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one U.S. citizen or qualified immigrant
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income eligibility
        income_eligible = spm_unit("nv_tanf_income_eligible", period)

        # Must meet resource eligibility ($10,000 limit)
        resource_eligible = spm_unit("nv_tanf_resource_eligible", period)

        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resource_eligible
        )
