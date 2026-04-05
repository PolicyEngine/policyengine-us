from policyengine_us.model_api import *


class nh_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for New Hampshire CCAP based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.07"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_employed = hours_worked > 0
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        individually_eligible = is_employed | is_student | is_disabled
        return spm_unit.sum(is_head_or_spouse & ~individually_eligible) == 0
