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
        person = spm_unit.members

        # Must meet demographic requirements (minor child OR pregnant woman)
        # Use federal demographic eligibility directly
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one citizen or legal immigrant
        # Use federal immigration eligibility
        immigration_status_eligible = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income requirements (gross and net income tests)
        income_eligible = spm_unit("ga_tanf_income_eligible", period)

        # Must meet resource requirements (assets <= $1,000)
        resources_eligible = spm_unit("ga_tanf_resources_eligible", period)

        # All requirements must be met
        return (
            demographic_eligible
            & immigration_status_eligible
            & income_eligible
            & resources_eligible
        )
