from policyengine_us.model_api import *


class nh_ccap_authorized_activity_hours(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    defined_for = StateCode.NH
    label = "New Hampshire CCAP authorized activity hours per week"
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.07"

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        hours = person("weekly_hours_worked", period.this_year)
        # He-C 6910.07(p): for two-parent households, use the lowest hours
        head_spouse_hours = where(is_head_or_spouse, hours, np.inf)
        return spm_unit.min(head_spouse_hours)
