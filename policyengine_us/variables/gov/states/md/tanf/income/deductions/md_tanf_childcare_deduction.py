from policyengine_us.model_api import *


# reference: https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0904%20Deductions%20and%20Expenses%20rev%2011.22.1.doc
#            page 1
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
        p = parameters(period).gov.states.md.tanf.income.deductions
        full_time = spm_unit.any(
            work_hours >= p.earnings_exclusion.fulltime_hours
        )

        return children * where(
            full_time,
            p.childcare_expenses.full_time,
            p.childcare_expenses.part_time,
        )
