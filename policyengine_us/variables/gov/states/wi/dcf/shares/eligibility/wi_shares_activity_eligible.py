from policyengine_us.model_api import *


class wi_shares_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Wisconsin Shares activity eligible"
    definition_period = MONTH
    defined_for = StateCode.WI
    reference = (
        "https://dcf.wisconsin.gov/wisconsin-shares/wisconsin-shares-handbook-july-2026#page=35",
        "https://docs.legis.wisconsin.gov/statutes/statutes/49/III/155/1m/a",
    )

    def formula(spm_unit, period, parameters):
        # Every parent in the assistance group must participate in an approved
        # activity for child care to be needed (Sections 4.8 and 5.1).
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        in_approved_activity = person("wi_shares_parent_in_approved_activity", period)
        has_head_or_spouse = spm_unit.sum(is_head_or_spouse) >= 1
        all_covered = spm_unit.sum(is_head_or_spouse & ~in_approved_activity) == 0
        modeled_eligible = has_head_or_spouse & all_covered
        # Fall back to the CCDF activity-test input for approved activities
        # not individually modeled, such as FSET job search or work
        # experience, Learnfare, and a temporary break from an approved
        # activity of up to three months (Section 5.1; Wis. Stat.
        # § 49.155(1m)(a)6.).
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return modeled_eligible | meets_ccdf
