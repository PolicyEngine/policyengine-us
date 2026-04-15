from policyengine_us.model_api import *


class vt_ccfap_meets_activity_test(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.VT
    label = "Vermont CCFAP service need test"
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/CDD/CCFAP/CCFAP-Regulations.pdf#page=7"

    def formula(spm_unit, period):
        person = spm_unit.members
        is_adult = person("is_adult", period)
        # Employment (II B 1 a) or Self Employment (II B 1 b)
        has_employment = person("employment_income", period.this_year) > 0
        has_self_employment = person("self_employment_income", period.this_year) > 0
        employed = spm_unit.any(is_adult & (has_employment | has_self_employment))
        # Training or Education (II B 1 e)
        in_training = spm_unit.any(
            is_adult & person("is_full_time_college_student", period.this_year)
        )
        # Special Health Need - Adult (II B 1 f)
        has_disabled_adult = spm_unit.any(is_adult & person("is_disabled", period))
        # Special Health Need - Child (II B 1 g)
        has_special_needs_child = spm_unit.any(
            ~is_adult & person("is_disabled", period)
        )
        # Fallback for non-derivable service needs
        # (seeking employment, parental leave, start-up self-employment,
        # family support child care)
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return (
            employed
            | in_training
            | has_disabled_adult
            | has_special_needs_child
            | fallback
        )
