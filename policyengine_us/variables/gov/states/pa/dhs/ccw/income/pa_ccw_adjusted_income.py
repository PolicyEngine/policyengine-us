from policyengine_us.model_api import *


class pa_ccw_adjusted_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Pennsylvania CCW adjusted annual family income"
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=18"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw.income
        gross = add(spm_unit, period, ["pa_ccw_countable_income"])
        stepparent_annual = (
            spm_unit("pa_ccw_stepparent_deduction", period.first_month) * MONTHS_IN_YEAR
        )
        alimony_paid = add(spm_unit, period, ["alimony_expense"])
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        medical_expenses = add(spm_unit, period, ["medical_out_of_pocket_expenses"])
        medical_deduction = max_(
            medical_expenses - gross * p.medical_expense_threshold, 0
        )
        return max_(
            gross
            - stepparent_annual
            - alimony_paid
            - child_support_paid
            - medical_deduction,
            0,
        )
