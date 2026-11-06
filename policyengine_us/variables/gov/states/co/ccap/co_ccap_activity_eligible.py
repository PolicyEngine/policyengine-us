from policyengine_us.model_api import *


class co_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Meets the Colorado Child Care Assistance Program activity requirement"
    definition_period = MONTH
    defined_for = StateCode.CO
    reference = (
        # 3.111(B)(1): caretakers must participate in an eligible activity.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=31",
        # 3.111(D)(1): eligible households with one or two caretakers.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=33",
        # 3.111(E): an incapacitated single caretaker with no activity.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=35",
        # 3.111(G): employment, self-employment, job search, education.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=36",
        # 3.116(A): Colorado Works participants.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=63",
        # 3.119(D): protective services households.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=69",
        # 3.121(B)(3): families experiencing homelessness.
        "https://www.sos.state.co.us/CCR/GenerateRulePdf.do?ruleVersionId=12658&fileName=8%20CCR%201403-1#page=72",
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
        # the floor.
        weeks = person("weeks_worked", year)
        weeks_at_work = where(weeks > 0, min_(weeks, WEEKS_IN_YEAR), WEEKS_IN_YEAR)
        # Pre-response hours avoid a circular dependency through labor supply
        # responses.
        annual_hours = person("weekly_hours_worked_before_lsr", year) * weeks_at_work
        wage_floor = parameters(period).gov.dol.minimum_wage * annual_hours
        works = (earnings > 0) & (earnings >= wage_floor)
        # 3.111(G)(4) covers post-secondary education, training and basic
        # education. The model can't see the lifetime week limits.
        in_activity = works | person("is_full_time_student", year)
        # 3.103(C) limits caretakers to the parents, guardians and those in loco
        # parentis who contribute to the child's welfare, so the filers who claim
        # an eligible child stand in for them. Another adult in the home doesn't
        # count. 3.111(D)(1)(b) treats a caretaker who is involuntarily out of
        # the home, as through incarceration, as absent.
        eligible_child = person("co_ccap_child_eligible", period)
        claims_eligible_child = person.tax_unit.sum(eligible_child) > 0
        caretaker = (
            person("is_tax_unit_head_or_spouse", year)
            & claims_eligible_child
            & ~person("is_incarcerated", period)
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
        # 3.116(A) treats Colorado Works participants in allowable work activities
        # as in an eligible activity. Enrollment stands in for the individualized
        # plan and referral.
        colorado_works = spm_unit("is_tanf_enrolled", period)
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
        # This input covers job search (3.111(G)(3)), part-time study, substance
        # use disorder treatment (3.111(G)(4)(a)(3)), the launch period for a new
        # business (3.111(G)(2)(e)), temporary leave (3.111(D)(8) and (9)) and
        # Child Welfare Child Care (3.120).
        other_activity = spm_unit("meets_ccdf_activity_test", year)
        return (
            low_income_activity
            | colorado_works
            | protective_services
            | homeless
            | other_activity
        )
