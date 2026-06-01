from policyengine_us.model_api import *


class ak_ccap_parent_in_eligible_activity(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Each parent meets Alaska CCAP activity requirement"
    definition_period = MONTH
    defined_for = StateCode.AK
    reference = "https://health.alaska.gov/media/igiccwuf/child-care-assistance-program-policies-and-procedures.pdf#page=184"

    def formula(spm_unit, period):
        # Manual §4070-3 D requires EACH parent to be engaged in an eligible
        # activity. We don't track job search, training, jury duty, or CC24
        # incapacity at the moment — fall back to the federal CCDF activity
        # test (meets_ccdf_activity_test) so units flagged there are
        # treated as meeting the AK requirement. We also don't check the
        # self-employment minimum-wage threshold at the moment.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        has_earning = (
            add(person, period, ["employment_income", "self_employment_income"]) > 0
        )
        hours_worked = person("weekly_hours_worked", period.this_year)
        is_student = person("is_full_time_student", period.this_year)
        individually_eligible = has_earning | (hours_worked > 0) | is_student
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_failing_parents = spm_unit.sum(is_head_or_spouse & ~individually_eligible)
        all_parents_qualify = (n_parents >= 1) & (n_failing_parents == 0)
        # Manual §4070-3 D requires each parent in the family to be in an eligible activity.
        # We fall back to the federal CCDF activity test for activities not separately modeled
        # (job search, training, CC24 incapacity), which can be slightly broader than Alaska's
        # strict "each parent" test. Documented simplification.
        fallback = spm_unit("meets_ccdf_activity_test", period.this_year)
        return all_parents_qualify | fallback
