from policyengine_us.model_api import *


class wa_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Washington TANF eligible"
    definition_period = MONTH
    reference = "https://app.leg.wa.gov/wac/default.aspx?cite=388-400-0005"
    defined_for = StateCode.WA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Must meet demographic requirements (minor child with deprived parent
        # OR pregnant woman)
        # Per WAC 388-400-0005, eligibility follows federal TANF demographic rules
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one U.S. citizen or qualified immigrant
        # Per WAC 388-424-0001, follows federal immigration eligibility
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income eligibility (gross earned income < limit)
        # Per WAC 388-478-0035
        income_eligible = spm_unit("wa_tanf_income_eligible", period)

        # Must meet resource eligibility (countable resources <= $6,000)
        # Per WAC 388-470-0045
        resources_eligible = spm_unit(
            "wa_tanf_resources_eligible", period.this_year
        )

        # All requirements must be met
        return (
            demographic_eligible
            & has_citizen
            & income_eligible
            & resources_eligible
        )
