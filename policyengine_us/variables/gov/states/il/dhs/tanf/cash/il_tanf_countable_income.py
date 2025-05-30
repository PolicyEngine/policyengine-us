from policyengine_us.model_api import *


class il_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois TANF countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        # For now, use a simplified calculation
        # This should be enhanced with IL-specific income disregards
        gross_earned = add(spm_unit, period, ["employment_income"])
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
        # Apply a simple 20% earned income disregard
        # This is a placeholder - actual IL rules may differ
        countable_earned = gross_earned * 0.8
        return countable_earned + gross_unearned
