from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    co_resident_parent_indices,
)


class co_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets the Colorado Child Care Assistance Program activity requirement"
    definition_period = MONTH
    defined_for = StateCode.CO
    reference = (
        # PDF pages 2, 31, 33-37, 39-40, 63, 68-69, 72
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=2",
        # 2023 edition, section 3.105.1
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=11042&fileName=8%20CCR%201403-1#page=14",
        "https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-98/subpart-C/section-98.20#p-98.20(a)(3)",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap.activity
        person = spm_unit.members
        year = period.this_year
        # Clip each source so a business loss can't erase wages.
        earnings = np.sum(
            [max_(person(source, year), 0) for source in p.earned_income_sources],
            axis=0,
        )
        # 3.111(G)(1)(b) and (G)(2)(d) require gross income of at least the
        # federal minimum wage for each hour worked. Weeks of zero mean none were
        # reported, so usual hours apply to the full year. A person with earnings
        # and no recorded hours passes, since no hours can pull the rate below
        # the floor. The model records one figure for weekly hours, so a job and
        # a business share it; meets_ccdf_activity_test covers a qualifying job
        # beside unpaid or loss-making work.
        weeks = person("weeks_worked", year)
        weeks_at_work = where(weeks > 0, min_(weeks, WEEKS_IN_YEAR), WEEKS_IN_YEAR)
        # Pre-response hours avoid a circular dependency through labor supply
        # responses.
        annual_hours = person("weekly_hours_worked_before_lsr", year) * weeks_at_work
        wage_floor = parameters(period).gov.dol.minimum_wage * annual_hours
        works = (earnings > 0) & (earnings >= wage_floor)
        # 3.111(G)(4) covers training, post-secondary education for a first
        # bachelor's degree or less, and basic education. The model can't see
        # the lifetime week limits.
        in_activity = works | person("co_ccap_in_eligible_education", year)
        # 3.103(C) limits caretakers to the parents, guardians and those in loco
        # parentis who contribute to the child's welfare, and 3.111(D)(2) counts
        # them whatever their tax filing. The filers who claim an eligible child
        # stand in for them, joined by any parent that the child's parent ids
        # name in the same SPM unit. Without parent ids, a parent who files
        # separately and claims no child doesn't count, and neither does another
        # adult in the home. 3.111(D)(1)(b) treats a caretaker who is
        # involuntarily out of the home, as through incarceration, as absent.
        eligible_child = person("co_ccap_child_eligible", period)
        claims_eligible_child = person.tax_unit.sum(eligible_child) > 0
        claiming_filer = (
            person("is_tax_unit_head_or_spouse", year) & claims_eligible_child
        )
        unit = spm_unit.members_entity_id
        children = np.flatnonzero(eligible_child)
        named_parents = []
        for parents in co_resident_parent_indices(person, year):
            parent = parents[children]
            resolved = parent >= 0
            same_unit = unit[np.where(resolved, parent, 0)] == unit[children]
            named_parents.append(parent[resolved & same_unit])
        named_parents = np.concatenate(named_parents)
        linked_parent = np.bincount(named_parents, minlength=person.count) > 0
        caretaker = (claiming_filer | linked_parent) & ~person(
            "is_incarcerated", period
        )
        # 3.111(D)(1)(c)(3) lets one caretaker be incapacitated when the other is
        # in an activity, and 3.111(E) bars a single incapacitated caretaker with
        # no activity. Disability stands in for the medical verification.
        incapacitated = person("is_disabled", year) | person(
            "is_incapable_of_self_care", year
        )
        has_active_caretaker = spm_unit.sum(caretaker & in_activity) > 0
        no_inactive_caretaker = (
            spm_unit.sum(caretaker & ~in_activity & ~incapacitated) == 0
        )
        low_income_activity = has_active_caretaker & no_inactive_caretaker
        # 3.118(A) and 3.119(D) exempt households with children placed in foster
        # or kinship care under an open child welfare case.
        protective_services = spm_unit.any(
            eligible_child
            & (
                person("receives_or_needs_protective_services", year)
                | person("is_in_foster_care", period)
            )
        )
        # 3.121(B)(3)(a) waives the activity during a stabilization period of at
        # least 60 days. The model can't track that period, so the exemption
        # lasts as long as the household's homeless flag.
        homeless = spm_unit.household("is_homeless", year)
        # This input covers job search (3.111(G)(3)), substance use disorder
        # treatment (3.111(G)(4)(a)(3)), the launch period for a new business
        # (3.111(G)(2)(e)), temporary leave (3.111(D)(8) and (9)), Child Welfare
        # Child Care (3.120) and Colorado Works participants in allowable work
        # activities under an individualized plan (3.116(A)). TANF receipt
        # alone doesn't count: under 3.111(D)(6) and 3.115(C), caretakers of
        # children who receive basic cash assistance without them must meet
        # the low-income activity test.
        other_activity = spm_unit("meets_ccdf_activity_test", year)
        return low_income_activity | protective_services | homeless | other_activity
