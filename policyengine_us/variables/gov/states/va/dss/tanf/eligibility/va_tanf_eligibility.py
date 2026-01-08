from policyengine_us.model_api import *


class va_tanf_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=1"

    def formula(spm_unit, period, parameters):
        demographic_eligible = spm_unit("is_demographic_tanf_eligible", period)
        income_eligible = spm_unit("va_tanf_income_eligibility", period)
        # At least one person must be a citizen or qualified noncitizen
        person = spm_unit.members
        citizenship_check = person(
            "is_citizen_or_legal_immigrant", period.this_year
        )
        has_eligible_member = spm_unit.any(citizenship_check)
        return demographic_eligible & income_eligible & has_eligible_member
