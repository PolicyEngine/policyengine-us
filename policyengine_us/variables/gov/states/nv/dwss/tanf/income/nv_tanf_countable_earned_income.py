from policyengine_us.model_api import *


class nv_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Nevada TANF countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/TANF/TANF_FAQ-Eligibility_Criteria-Income-Consid-1/"
    defined_for = StateCode.NV

    def formula(spm_unit, period, parameters):
        # Per Nevada DSS: Work expense deduction is greater of $90 or 20%
        p = parameters(period).gov.states.nv.dwss.tanf.income.disregard
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])

        # Calculate work expense deduction: max of flat amount or percentage
        flat_deduction = p.work_expense_flat_amount
        percentage_deduction = gross_earned * p.work_expense_rate
        work_expense_deduction = max_(flat_deduction, percentage_deduction)

        # NOTE: Nevada has graduated earned income disregards (100%/85%/75%/65%)
        # that decrease over 12 months. PolicyEngine cannot track employment
        # duration, so we apply only the work expense deduction.
        return max_(gross_earned - work_expense_deduction, 0)
