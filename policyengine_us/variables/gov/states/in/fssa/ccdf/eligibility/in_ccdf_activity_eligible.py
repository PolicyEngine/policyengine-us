from policyengine_us.model_api import *


class in_ccdf_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Indiana CCDF activity eligible"
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/carefinder/files/CCDF-Policy-Manual.pdf#page=15"
    )

    def formula(spm_unit, period, parameters):
        # Both the applicant and co-applicant must demonstrate a valid service
        # need. There is no minimum number of working hours required.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        in_eligible_activity = person("in_ccdf_parent_in_eligible_activity", period)
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~in_eligible_activity) == 0
        return has_head_or_spouse & all_covered
