from policyengine_us.model_api import *


class md_tanf_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF childcare deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        children = spm_unit("md_tanf_count_children", period)
        person = spm_unit.members
        work_hours = person("work_hours_per_week", period)
        # Get the policy parameters.
        p1 = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        p2 = parameters(
            period
        ).gov.states.md.tanf.income.deductions.childcare_expenses
        full_time = spm_unit.any(work_hours >= p1.fulltime_hours)

        return children * where(
            full_time,
            p2.full_time,
            p2.part_time,
        )
