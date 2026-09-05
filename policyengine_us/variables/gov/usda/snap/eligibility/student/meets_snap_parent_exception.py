from policyengine_us.model_api import *


class meets_snap_parent_exception(Variable):
    value_type = bool
    entity = Person
    label = "Meets SNAP student parent exception"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#e_5",
        "https://www.law.cornell.edu/uscode/text/7/2015#e_8",
        "https://www.law.cornell.edu/cfr/text/7/273.5",
        "https://fhb.hhs.texas.gov/handbooks/texas-works-handbook/b-410-students-higher-education",
        "https://policies.ncdhhs.gov/wp-content/uploads/fss235-1.pdf#page=2",
        "https://www.dshs.wa.gov/esa/eligibility-z-manual-ea-z/student-status",
        "https://dssmanuals.mo.gov/food-stamps/1135-000-00/1135-025-00/",
        "https://ncdhhs.gov/fns-students-higher-education/download?attachment=",
        "https://www.dhs.state.il.us/page.aspx?item=13276",
    )

    def formula(person, period, parameters):
        # Exception 5: parent responsible for a dependent child under 6
        # (child 6-11 without adequate child care is not modeled)
        # Exception 8: single parent enrolled full-time with a child under 12
        is_parent = person("is_tax_unit_head_or_spouse", period)
        spm_unit = person.spm_unit
        tax_unit = person.tax_unit
        parent_count = spm_unit.sum(is_parent)

        p = parameters(period).gov.usda.snap.student
        spm_unit_ages = spm_unit.members("age", period)
        tax_unit_ages = tax_unit.members("age", period)
        young_child_limit = p.child_age_limit.two_parent
        has_young_child = spm_unit.any(spm_unit_ages < young_child_limit)
        tax_unit_young_child_count = tax_unit.sum(tax_unit_ages < young_child_limit)
        has_child_under_single_parent_limit = spm_unit.any(
            spm_unit_ages < p.child_age_limit.single_parent
        )

        is_full_time_student = person("is_full_time_college_student", period)
        is_higher_ed_student = person("is_snap_higher_ed_student", period)
        state = person.household("state_code_str", period)
        # 7 CFR 273.5(b)(8) is silent on shared care. Some states let each
        # child under six exempt one adult, Missouri and Illinois one adult
        # per household; the rest keep the uncapped federal reading. Claims
        # go first to student parents with no other exception, then in
        # member order, and per-child claims stay within the child's tax
        # unit.
        cap = p.child_care_claim_cap
        caps_per_child = cap.per_child[state].astype(bool)
        caps_per_household = cap.per_household[state].astype(bool)
        needs_claim = is_higher_ed_student & ~person(
            "meets_snap_non_parent_student_exception", period
        )
        claim_order = where(needs_claim, 0, 1)
        tax_unit_rank = person.get_rank(tax_unit, claim_order, is_parent)
        household_rank = person.get_rank(
            spm_unit, claim_order, is_parent & (tax_unit_young_child_count > 0)
        )
        gets_claim = select(
            [caps_per_household, caps_per_child],
            [household_rank < 1, tax_unit_rank < tax_unit_young_child_count],
            default=True,
        )
        # Some states presume a non-student parent who is not working
        # provides the care, which defeats the student's claim.
        hours_worked = person("weekly_hours_worked_before_lsr", period)
        presumed_caregiver = is_parent & ~is_higher_ed_student & (hours_worked == 0)
        caregiver_defeats_claim = (
            p.non_student_parent_presumed_caregiver[state].astype(bool)
            & is_higher_ed_student
            & tax_unit.any(presumed_caregiver)
        )
        exception_5 = has_young_child & gets_claim & ~caregiver_defeats_claim
        # Exception 8: single parent enrolled full-time, child under 12.
        exception_8 = (
            (parent_count == 1)
            & has_child_under_single_parent_limit
            & is_full_time_student
        )
        return is_parent & (exception_5 | exception_8)
