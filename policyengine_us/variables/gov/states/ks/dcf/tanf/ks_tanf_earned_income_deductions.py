from policyengine_us.model_api import *


class ks_tanf_earned_income_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF earned income deductions"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://content.dcf.ks.gov/ees/keesm/robo10-17/keesm8151.htm",
        "https://content.dcf.ks.gov/ees/keesm/implem_memo/2008_0326_TAF_ei_disregard.htm",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per KEESM 8151: First deduct $90 work expense per employed person
        # Per KEESM Memo 2008-0326: Then apply 60% disregard to remainder
        # Total deductions = work_expense + (gross - work_expense) * 0.60
        p = parameters(period).gov.states.ks.dcf.tanf
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        # Apply $90 work expense (capped at gross earned)
        work_expense = min_(gross_earned, p.work_expense_deduction.amount)
        earned_after_work_expense = max_(gross_earned - work_expense, 0)
        # Apply 60% disregard to remainder
        disregard = earned_after_work_expense * p.earned_income_disregard.rate
        return work_expense + disregard
