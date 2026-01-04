from policyengine_us.model_api import *


class id_tafi_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho TAFI eligible"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.100",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.08.254",
    )
    defined_for = StateCode.ID

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.tafi
        # Demographic eligibility - use federal baseline (IDAPA 16.03.08.125)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Immigration eligibility - use federal baseline (IDAPA 16.03.08.131)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )

        # Resources eligibility (IDAPA 16.03.08.200)
        resources_eligible = spm_unit("id_tafi_resources_eligible", period)

        # Income eligibility - grant calculation must result in positive amount
        grant_standard = spm_unit("id_tafi_grant_standard", period)
        income_eligible = grant_standard > 0

        return (
            demographic_eligible
            & immigration_eligible
            & resources_eligible
            & income_eligible
        )
