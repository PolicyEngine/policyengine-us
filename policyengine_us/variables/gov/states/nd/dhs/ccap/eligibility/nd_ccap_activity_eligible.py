from policyengine_us.model_api import *


class nd_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "North Dakota CCAP activity eligible"
    definition_period = MONTH
    defined_for = StateCode.ND
    reference = "https://www.nd.gov/dhs/policymanuals/40028/40028.htm"

    def formula(spm_unit, period, parameters):
        # All caretakers (head and spouse) must be in an allowable activity.
        # Requiring every caretaker to be active also serves as the proxy for
        # the two-caretaker availability rule (NDAC 75-02-01.3-11): if a
        # caretaker is available (not in an activity), the unit is ineligible.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        in_eligible_activity = person("nd_ccap_parent_in_eligible_activity", period)
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~in_eligible_activity) == 0
        modeled_eligible = has_head_or_spouse & all_covered
        # Fall back to the CCDF activity-test input for approved activities not
        # individually modeled (job search, education or training programs,
        # SNAP E&T, or a temporary leave from work or school; 400-28-55-05).
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return modeled_eligible | meets_ccdf
