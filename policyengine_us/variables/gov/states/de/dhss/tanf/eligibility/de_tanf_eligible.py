from policyengine_us.model_api import *


class de_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Delaware TANF"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/delaware/16-Del-Admin-Code-SS-4000-4008",
        "https://dhss.delaware.gov/dss/tanf/",
    )
    defined_for = StateCode.DE

    def formula(spm_unit, period, parameters):
        # Use federal demographic eligibility (minor child or pregnant)
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        # Delaware follows federal immigration rules
        immigration_eligible = (
            add(spm_unit, period, ["is_citizen_or_legal_immigrant"]) > 0
        )
        # State-specific eligibility tests
        gross_income_eligible = spm_unit(
            "de_tanf_gross_income_eligible", period
        )
        net_income_eligible = spm_unit("de_tanf_net_income_eligible", period)
        resources_eligible = spm_unit("de_tanf_resources_eligible", period)

        return (
            demographic_eligible
            & immigration_eligible
            & gross_income_eligible
            & net_income_eligible
            & resources_eligible
        )
