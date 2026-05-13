from policyengine_us.model_api import *


class pa_ccw_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Pennsylvania CCW based on activity requirements"
    # YEAR: PA evaluates activity at annual redetermination.
    # Eligibility continues through the 12-month certification period
    # after a break in work, education, or training (55 Pa. Code 3042.19).
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=15"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw.activity_requirements
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        hours_worked = person("weekly_hours_worked", period)
        meets_work_requirement = hours_worked >= p.weekly_hours
        age = person("age", period)
        is_student = person("is_full_time_student", period)
        is_teen_parent_student = is_student & (age < p.teen_parent_max_age)
        # Training combo: employment + education/training combined,
        # with at least 10 hrs/week of work (55 Pa. Code 3042.33).
        meets_training_combo = (
            hours_worked >= p.training_combo_min_work_hours
        ) & is_student
        individually_eligible = (
            meets_work_requirement | is_teen_parent_student | meets_training_combo
        )
        # Fallback for non-derivable activities (job search, DV waiver, etc.)
        fallback = spm_unit("meets_ccdf_activity_test", period)
        # All parents must qualify (55 Pa. Code 3042.33).
        n_parents = spm_unit.sum(is_head_or_spouse)
        n_qualifying = spm_unit.sum(is_head_or_spouse & individually_eligible)
        return (n_qualifying >= n_parents) | fallback
