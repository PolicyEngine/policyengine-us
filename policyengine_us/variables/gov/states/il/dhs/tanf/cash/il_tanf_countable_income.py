from policyengine_us.model_api import *


class il_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.tanf.cash
        
        # Calculate gross earned income
        gross_earned = add(spm_unit, period, ["employment_income"])
        
        # Calculate gross unearned income
        gross_unearned = add(
            spm_unit,
            period,
            [
                "social_security",
                "ssi",
                "unemployment_compensation",
                "pension_income",
                "interest_income",
                "dividend_income",
            ],
        )
        
        # Apply Illinois earned income deduction (75% of earned income is disregarded)
        earned_income_deduction_rate = p.amount.deductions.earnings.percent
        countable_earned = gross_earned * (1 - earned_income_deduction_rate)
        
        return countable_earned + gross_unearned
