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
        "https://dssmanuals.mo.gov/food-stamps/1135-000-00/1135-025-00/",
    )

    def formula(person, period, parameters):
        # Heads/spouses and the SPM unit remain proxies for caregivers and
        # the SNAP household; actual care relationships are not observed.
        is_parent = person("is_tax_unit_head_or_spouse", period)
        spm_unit = person.spm_unit
        parent_count = spm_unit.sum(is_parent)

        p = parameters(period).gov.usda.snap.student
        spm_unit_ages = spm_unit.members("age", period)
        young_child_limit = p.child_age_limit.two_parent
        young_child_count = spm_unit.sum(spm_unit_ages < young_child_limit)
        has_child_under_single_parent_limit = spm_unit.any(
            spm_unit_ages < p.child_age_limit.single_parent
        )

        is_full_time_student = person("is_full_time_college_student", period)
        is_higher_ed_student = person("is_snap_higher_ed_student", period)
        state = person.household("state_code_str", period)
        cap = p.child_care_claim_cap
        caps_per_household = cap.per_household[state].astype(bool)
        needs_claim = is_higher_ed_student & ~person(
            "meets_snap_non_parent_student_exception", period
        )
        # Allocate to students needing this exception, then member order.
        # This is a modeling assumption, not a determination of actual care.
        claim_rank = person.get_rank(spm_unit, where(needs_claim, 0, 1), is_parent)
        # States without the cap keep the uncapped federal reading.
        gets_claim = ~caps_per_household | (claim_rank == 0)
        # Exception numbers follow 7 U.S.C. 2015(e); 7 CFR 273.5(b) orders
        # them differently (the under-six exception is (b)(8) there).
        # Exception 5; care of children 6-11 without adequate care is not modeled.
        exception_5 = (young_child_count > 0) & gets_claim
        # Exception 8: single parent enrolled full-time, child under 12.
        exception_8 = (
            (parent_count == 1)
            & has_child_under_single_parent_limit
            & is_full_time_student
        )
        return is_parent & (exception_5 | exception_8)
