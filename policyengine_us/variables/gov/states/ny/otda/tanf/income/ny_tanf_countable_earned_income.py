from policyengine_us.model_api import *


class ny_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NY

    def formula(spm_unit, period, parameters):
        # Get gross earned income.
        gross_earned_income = spm_unit("ny_tanf_gross_earned_income", period)
        # Multiply by 100% minus the EID.
        p = parameters(
            period
        ).gov.states.ny.otda.tanf.income.earned_income_deduction
        # https://otda.ny.gov/policy/gis/2022/22DC085.pdf Section 2
        # Effective October 1, 2022, the EID will be applied prior to the work expense disregard.
        return max_(
            gross_earned_income * (1 - p.percent) - p.flat * MONTHS_IN_YEAR,
            0,
        )
