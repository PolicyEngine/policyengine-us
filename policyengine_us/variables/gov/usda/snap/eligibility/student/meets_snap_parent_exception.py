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
    )

    def formula(person, period, parameters):
        # Exception 5: Parent with responsibility for dependent child under 6,
        # Or child 6-11 when adequate child care is not available (not modeled)
        # Exception 8: Single parent enrolled full-time with responsibility
        # for dependent child under 12
        is_parent = person("is_tax_unit_head_or_spouse", period)
        spm_unit = person.spm_unit
        parent_count = spm_unit.sum(is_parent)

        # Check if there are children in the household under the age thresholds
        p = parameters(period).gov.usda.snap.student
        household_member_ages = spm_unit.members("age", period)
        young_child_count = spm_unit.sum(
            household_member_ages < p.child_age_limit.two_parent
        )
        has_child_under_single_parent_limit = spm_unit.any(
            household_member_ages < p.child_age_limit.single_parent
        )

        is_full_time_student = person("is_full_time_college_student", period)
        # Exception 5: a parent responsible for a child under 6 (the
        # two-parent age limit); no full-time enrollment requirement.
        # 7 CFR 273.5(b)(8) is silent on shared care. Some state manuals let
        # each child under six exempt only one adult (Texas Works Handbook
        # B-412(7); North Carolina FNS 235.04(E); Washington EA-Z Student
        # Status), and Missouri and Illinois cap the claim at one adult per
        # household. Other states keep the uncapped federal reading. We
        # cannot observe who provides most of the care, so the claims go
        # first to the parents who need them: higher-education students
        # with no other exception (North Carolina's student guidance: "The
        # other parent would need to be evaluated for another exemption").
        # Remaining parents follow in member order.
        state = person.household("state_code_str", period)
        cap = p.child_care_claim_cap
        caps_per_child = cap.per_child[state].astype(bool)
        caps_per_household = cap.per_household[state].astype(bool)
        needs_claim = person("is_snap_higher_ed_student", period) & ~person(
            "meets_snap_non_parent_student_exception", period
        )
        claim_order = where(needs_claim, 0, 1)
        claim_rank = person.get_rank(spm_unit, claim_order, is_parent)
        claim_limit = select(
            [caps_per_household, caps_per_child],
            [1, young_child_count],
            default=parent_count,
        )
        exception_5 = (young_child_count > 0) & (claim_rank < claim_limit)
        # Exception 8: single parent enrolled full-time, responsible for a
        # child under 12 (the single-parent age limit).
        exception_8 = (
            (parent_count == 1)
            & has_child_under_single_parent_limit
            & is_full_time_student
        )
        parent_exception_requirement = exception_5 | exception_8

        return is_parent & parent_exception_requirement
