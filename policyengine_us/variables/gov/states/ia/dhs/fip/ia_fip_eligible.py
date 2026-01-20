from policyengine_us.model_api import *


class ia_fip_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Iowa FIP eligible"
    definition_period = YEAR
    defined_for = StateCode.IA
    reference = (
        "https://www.legis.iowa.gov/docs/iac/chapter/01-07-2026.441.41.pdf"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.fip.eligibility
        # Must have at least one eligible child (uses federal demographic rules)
        has_children = spm_unit("is_demographic_tanf_eligible", period)
        # Must meet immigration status eligibility (citizen or qualified alien)
        # Per Iowa legal code 441—41.23(239B), 41.23(5)
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        current_recipient = spm_unit("is_tanf_enrolled", period)
        limit = where(
            current_recipient,
            p.resource_limit_recipient,
            p.resource_limit_applicant,
        )
        resources = spm_unit("spm_unit_assets", period.this_year)
        resource_eligible = resources <= limit
        income_eligible = spm_unit("ia_fip_income_eligible", period)

        return (
            has_children
            & immigration_eligible
            & resource_eligible
            & income_eligible
        )
