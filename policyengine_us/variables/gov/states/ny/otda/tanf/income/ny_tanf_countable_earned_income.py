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
        gross_earned_income=spm_unit("ny_tanf_gross_earned_income", period)        
        # Multiply by 100% minus the EID.
        p = parameters(period).gov.states.ny.otda.tanf
        return gross_earned_income * (1 - p.income.earned_income_deduction)
