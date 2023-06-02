from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.md.tanf.md_tanf_count_children import (
    md_tanf_count_children,
)


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
        p = parameters(
            period
        ).gov.states.md.tanf.income.deductions.earnings_exclusion
        full_time = spm_unit.any(work_hours >= p.fulltime_hours)

        return children * where(
            full_time,
            p.fulltime_childcare_expenses,
            p.parttime_childcare_expenses,
        )
