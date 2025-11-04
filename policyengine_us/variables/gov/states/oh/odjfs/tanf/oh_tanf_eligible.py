from policyengine_us.model_api import *


class oh_tanf_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio TANF eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-10",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Must meet demographic requirements (minor child with parent/relative
        # OR pregnant woman at least 6 months pregnant)
        # Use federal demographic eligibility
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)

        # Must have at least one citizen or legal immigrant
        # Use federal immigration eligibility
        has_citizen = spm_unit.any(
            person("is_citizen_or_legal_immigrant", period)
        )

        # Must meet income requirements (countable income < payment standard)
        income_eligible = spm_unit("oh_tanf_income_eligible", period)

        # Ohio has NO resource limits per working_references.md:
        # "No Resource Test: Resources such as a car or home ownership
        # are NOT considered in determining eligibility"

        # All requirements must be met
        return demographic_eligible & has_citizen & income_eligible
