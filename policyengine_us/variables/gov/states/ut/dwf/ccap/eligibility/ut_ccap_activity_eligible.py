from policyengine_us.model_api import *


class ut_ccap_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Utah CCAP activity eligible"
    definition_period = MONTH
    defined_for = StateCode.UT
    reference = (
        "https://www.law.cornell.edu/regulations/utah/Utah-Admin-Code-R986-700-709"
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ut.dwf.ccap.eligibility
        person = spm_unit.members
        # R986-700-702(2) makes CC available to parents, specified
        # relatives, and court-appointed guardians, and R986-700-709
        # applies its work requirements to that client. is_parent (own
        # children in the household) identifies parent clients across
        # tax-unit boundaries and keeps minor parents visible, matching
        # the countable income scope of R986-700-710(4)(a); when no parent
        # lives in the household, the tax-unit head or spouse proxies the
        # nonparent caretaker client. Co-resident adults who are not the
        # client stay excluded from the hours test. Foster parents
        # receiving DHHS foster care reimbursement are eligible clients
        # (R986-700-702(2)(a)) subject to the same work requirements as
        # any other client, so is_parent correctly includes them and no
        # foster-parent carve-out applies.
        is_parent = person("is_parent", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        no_parent_present = spm_unit.sum(is_parent) == 0
        is_client = is_parent | (
            spm_unit.project(no_parent_present) & is_head_or_spouse
        )
        # weekly_hours_worked_before_lsr avoids the labor-supply feedback loop
        # that weekly_hours_worked (before_lsr + behavioral response) creates
        # in reform runs.
        hours = person("weekly_hours_worked_before_lsr", period.this_year)
        client_count = spm_unit.sum(is_client)
        lowest_client_hours = spm_unit.min(where(is_client, hours, np.inf))
        highest_client_hours = spm_unit.max(where(is_client, hours, 0))
        # A single parent must be employed an average of at least 15 hours
        # per week (R986-700-709(2)(a)(i)); in a two-parent household, one
        # parent must average at least 30 hours per week and the other at
        # least 15 (R986-700-709(2)(b)(i)(A)). The requirement that earnings
        # equal at least the minimum wage for the hours worked
        # (R986-700-709(2)) is not modeled.
        single_parent_eligible = highest_client_hours >= p.single_parent_min_hours
        both_parents_working_eligible = (
            highest_client_hours >= p.two_parent_second_min_hours
        ) & (lowest_client_hours >= p.two_parent_first_min_hours)
        # A two-parent household also qualifies when one parent is employed
        # and the other parent cannot provide care for the child because of
        # a physical, emotional, or mental incapacity (R986-700-709(2)(b)(i)(B)
        # and (4)(a)(iii)); is_disabled proxies the Department-verified
        # incapacity. The pathway is activity-linked: every non-disabled
        # parent must meet the single-parent hours requirement and at least
        # one parent must meet it, so a household of only non-working
        # disabled parents does not qualify.
        is_disabled = person("is_disabled", period.this_year)
        has_disabled_parent = spm_unit.any(is_client & is_disabled)
        able_parent_below_hours = (
            is_client & ~is_disabled & (hours < p.single_parent_min_hours)
        )
        incapacitated_parent_eligible = (
            has_disabled_parent
            & (spm_unit.sum(able_parent_below_hours) == 0)
            & single_parent_eligible
        )
        two_parent_eligible = (
            both_parents_working_eligible | incapacitated_parent_eligible
        )
        hours_eligible = select(
            [client_count == 1, client_count > 1],
            [single_parent_eligible, two_parent_eligible],
            default=False,
        )
        # Fall back to the CCDF activity-test input for approved activities
        # not individually modeled, such as the education and training
        # pathway (R986-700-711).
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        return hours_eligible | meets_ccdf
