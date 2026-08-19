from policyengine_us.model_api import *


class or_erdc_caretaker_weekly_need_hours(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = MONTH
    unit = "hour"
    label = "Oregon ERDC caretaker weekly child care need hours"
    defined_for = StateCode.OR
    reference = (
        "https://secure.sos.state.or.us/oard/view.action?ruleNumber=414-175-0023",
        "https://sharedsystems.dhsoha.state.or.us/DHSForms/Served/de2818.pdf#page=428",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        is_caretaker = person("is_tax_unit_head_or_spouse", period.this_year)
        # OAR 414-175-0023(5) sets hours from the caretaker's allowable child
        # care need. We proxy that need with work hours before labor supply
        # responses (avoiding a circular dependency); education, training, and
        # study hours are not separately tracked. For two-caretaker units the
        # OPEN worker guide (p. 428) counts only hours when both caretakers'
        # work or school schedules overlap; we do not track schedules, so we
        # use the lowest caretaker's hours, the maximum possible overlap.
        # Set this variable directly when actual overlapping hours are known.
        weekly_hours = person("weekly_hours_worked_before_lsr", period.this_year)
        # OAR 414-175-0023(1)(b)(A) excuses a second caretaker who is unable to
        # provide adequate care (proxied by disability, mirroring
        # or_erdc_activity_eligible); drop them from the overlap minimum so a
        # non-working excused caretaker does not collapse the need to zero. The
        # excuse is only for a second caretaker, so a lone disabled caretaker is
        # still counted.
        caretaker_count = spm_unit.sum(is_caretaker)
        multiple_caretakers = spm_unit.project(caretaker_count > 1)
        unable_to_care = person("is_disabled", period.this_year)
        counted_caretaker = is_caretaker & ~(multiple_caretakers & unable_to_care)
        # Non-caretakers and excused caretakers get infinity so they never lower
        # the need; if every caretaker is excused, fall back to zero.
        has_counted_caretaker = spm_unit.sum(counted_caretaker) > 0
        lowest_caretaker_hours = spm_unit.min(
            where(counted_caretaker, weekly_hours, np.inf)
        )
        return where(has_counted_caretaker, lowest_caretaker_hours, 0)
