from policyengine_us.model_api import *


class ky_ktap_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kentucky K-TAP countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://apps.legislature.ky.gov/law/kar/titles/921/002/016/"
    defined_for = StateCode.KY

    def formula(spm_unit, period, parameters):
        # Per 921 KAR 2:016 Section 5(3):
        # (a) Deduct $175 work expense from gross earned income
        # (b) Deduct dependent care expenses up to limits
        # (e) Apply 50% earned income disregard for 6 months
        p = parameters(period).gov.states.ky.dcbs.ktap.income.deductions
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        after_work_expense = max_(gross_earned - p.work_expense, 0)
        dependent_care = spm_unit("ky_ktap_dependent_care_disregard", period)
        after_dependent_care = max_(after_work_expense - dependent_care, 0)
        return after_dependent_care * (1 - p.earned_income_disregard_rate)
