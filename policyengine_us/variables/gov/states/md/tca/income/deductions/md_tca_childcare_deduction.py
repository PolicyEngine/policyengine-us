from policyengine_us.model_api import *


class md_tca_childcare_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TCA childcare deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dsd.maryland.gov/regulations/Pages/07.03.03.13.aspx"

    def formula(spm_unit, period, parameters):
        # Per COMAR 07.03.03.13, childcare deduction is only available
        # for households with children. The deduction is based on the
        # employment hours of the assistance unit member.
        has_children = spm_unit("is_demographic_tanf_eligible", period)
        person = spm_unit.members
        work_hours = person("weekly_hours_worked", period.this_year)
        p = parameters(period).gov.states.md.tca.income.deductions
        full_time = spm_unit.any(work_hours >= p.earned.fulltime_hours)

        deduction = where(
            full_time,
            p.childcare_expenses.full_time,
            p.childcare_expenses.part_time,
        )
        return where(has_children, deduction, 0)
