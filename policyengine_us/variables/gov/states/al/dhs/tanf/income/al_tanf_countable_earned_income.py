from policyengine_us.model_api import *


class al_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama TANF countable earned income"
    definition_period = MONTH
    reference = "https://admincode.legislature.state.al.us/api/chapter/660-2-2"
    defined_for = StateCode.AL

    def formula(spm_unit, period, parameters):
        # Per Ala. Admin. Code r. 660-2-2-.30(2) (effective 05/15/2022), earned
        # income deductions are: (a) disregard all earnings from timely reported
        # new employment for the first twelve months, then thereafter (b) deduct
        # the first 30% of gross earnings, and (c) child care / incapacitated
        # adult care costs.
        #
        # The 12-month new-employment disregard in (a) depends on how long each
        # earner has held their current job, which is not available in the input
        # data, so it is not modeled here; this assumes established (>12-month)
        # employment, under which only the 30% work expense and care-cost
        # deductions in (b) and (c) apply.
        p = parameters(period).gov.states.al.dhs.tanf.income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        work_expense = gross_earned * p.work_expense_rate
        # Per r. 660-2-2-.30(2)(c), the cost (on an as-paid basis) of child
        # care or care for an incapacitated adult living in the same home
        # and receiving FA is deducted from earned income, with no cap.
        childcare_expenses = spm_unit("childcare_expenses", period)
        adult_care_expenses = add(spm_unit, period, ["care_expenses"])
        return max_(
            gross_earned - work_expense - childcare_expenses - adult_care_expenses,
            0,
        )
