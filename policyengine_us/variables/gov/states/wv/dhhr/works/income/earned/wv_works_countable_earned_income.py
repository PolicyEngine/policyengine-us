from policyengine_us.model_api import *


class wv_works_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "West Virginia WV Works countable earned income"
    unit = USD
    definition_period = MONTH
    reference = "https://bfa.wv.gov/media/39948/download?inline#page=590"
    defined_for = StateCode.WV

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wv.dhhr.works.income
        # Step 1: Add together the countable gross earned income
        gross_earned = add(spm_unit, period, ["tanf_gross_earned_income"])
        # Step 2: Subtract 40% (Earned Income Disregard)
        after_disregard = gross_earned * (1 - p.earned_income_disregard.rate)
        # Step 3: Subtract Dependent Care Deduction (no maximum, per Section
        # 4.5.2.A.2, which covers dependent child or incapacitated adult care)
        dependent_care = spm_unit("childcare_expenses", period) + add(
            spm_unit, period, ["care_expenses"]
        )
        return max_(after_disregard - dependent_care, 0)
