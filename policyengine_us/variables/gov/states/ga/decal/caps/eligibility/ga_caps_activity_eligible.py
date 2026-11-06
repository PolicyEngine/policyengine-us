from policyengine_us.model_api import *


class ga_caps_activity_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Georgia CAPS based on activity requirements"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=33",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=2",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/07-CAPS_Policy-Priority%20Groups.pdf#page=8",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.activity_requirements
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        # Use pre-labor-supply-response hours to avoid a CAPS → net income →
        # labor supply response → hours → CAPS circularity (mirrors SNAP).
        hours_worked = person("weekly_hours_worked_before_lsr", period.this_year)
        meets_work_requirement = hours_worked >= p.weekly_hours
        # Per Policy Manual §6.8.1.1, the student exemption applies to parents
        # age 20 or younger; parents 21+ get a 2x credit-hour conversion but
        # must still meet the 24-hour weekly total. We don't track credit hours
        # or distinguish the student-age cap at the moment, so any full-time
        # student is treated as exempt.
        is_student = person("is_full_time_student", period.this_year)
        is_disabled = person("is_disabled", period.this_year)
        # Per Policy Manual §6.8.1.8, the disability exemption is two-parent
        # specific — a disabled parent is exempt and authorization is based on
        # the non-disabled parent's activity. We apply it more broadly to any
        # disabled head/spouse since restricting to two-parent units would
        # require modeling household composition more granularly than we
        # currently do.
        individually_eligible = meets_work_requirement | is_student | is_disabled
        all_heads_meet = ~spm_unit.any(is_head_or_spouse & ~individually_eligible)
        meets_ccdf = spm_unit("meets_ccdf_activity_test", period.this_year)
        # CAPS/00-7 waives the requirement for foster parents of children in DFCS
        # custody (7.5) and for parents in Grandparents Raising Grandchildren
        # (7.13). The Child Protective Services waiver in 7.4 is discretionary
        # ("may be waived"), so meets_ccdf_activity_test carries it as an input.
        has_dfcs_custody_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        grandparents_raising_grandchildren = spm_unit(
            "ga_caps_grandparents_raising_grandchildren", period
        )
        return (
            all_heads_meet
            | meets_ccdf
            | has_dfcs_custody_child
            | grandparents_raising_grandchildren
        )
