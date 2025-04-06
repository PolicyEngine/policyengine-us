from policyengine_us.model_api import *


class pa_tanf_personal_expense_full_time_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Pennsylvania TANF full time employment requirement"
    definition_period = YEAR
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        p = parameters(
            period
        ).gov.states.pa.tanf.income.earned_deduction.personal_expenses

        work_hours = person("work_hours_per_week", period)
        return spm_unit.any(work_hours >= p.full_time_employment)
