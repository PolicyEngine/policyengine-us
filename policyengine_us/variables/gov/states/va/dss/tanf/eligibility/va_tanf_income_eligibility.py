from policyengine_us.model_api import *


class va_tanf_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA TANF income eligibility"
    definition_period = MONTH
    defined_for = StateCode.VA
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=47"

    def formula(spm_unit, period, parameters):
        # Two-step income test per Virginia TANF Manual Section 305.1
        # Step 1: Gross income <= Need Standard
        gross_income = spm_unit("va_tanf_gross_income", period)
        need_standard = spm_unit("va_tanf_need_standard", period)
        step1_pass = gross_income <= need_standard

        # Step 2: Countable income (after all deductions) <= Grant Standard
        countable_income = spm_unit("va_tanf_countable_income", period)
        # Use appropriate grant standard based on UP eligibility
        up_eligible = spm_unit("va_up_tanf_eligibility", period)
        grant_standard = spm_unit("va_tanf_grant_standard", period)
        up_grant_standard = spm_unit("va_tanf_up_grant_standard", period)
        applicable_grant = where(
            up_eligible, up_grant_standard, grant_standard
        )
        step2_pass = countable_income <= applicable_grant

        return step1_pass & step2_pass
