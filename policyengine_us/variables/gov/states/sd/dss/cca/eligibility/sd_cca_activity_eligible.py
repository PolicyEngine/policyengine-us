from policyengine_us.model_api import *


class sd_cca_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "South Dakota CCA activity eligible"
    definition_period = MONTH
    defined_for = StateCode.SD
    reference = (
        "https://dss.sd.gov/docs/childcare/assistance/Subsidy_Manual.pdf#page=8",
        "https://sdlegislature.gov/Rules/Administrative/67:47:01:03",
    )

    def formula(spm_unit, period, parameters):
        # Every caretaker (head and spouse) must be in an approved activity
        # (employment, self-employment, or school). Requiring every caretaker
        # to be active also serves as the proxy for the availability rule: if a
        # caretaker is available (not in an activity), the unit is ineligible.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        in_eligible_activity = person("sd_cca_parent_in_eligible_activity", period)
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~in_eligible_activity) == 0
        modeled_eligible = has_head_or_spouse & all_covered
        # Fall back to the CCDF activity-test input for approved activities not
        # individually modeled (job search, education or training programs).
        # Protective services is handled per child in
        # sd_cca_reason_for_care_eligible, not here.
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return modeled_eligible | meets_ccdf
