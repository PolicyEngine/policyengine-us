from policyengine_us.model_api import *


class ny_liheap_vulnerable_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "NY HEAP vulnerable household supplement amount"
    definition_period = YEAR
    defined_for = "ny_liheap_income_eligible"
    unit = USD
    documentation = "Additional HEAP benefit for vulnerable households"

    def formula(spm_unit, period, parameters):
        # NY HEAP program year starts November 2024
        if period.start.year < 2025:
            return 0

        p = parameters(period).gov.states.ny.otda.liheap.benefit

        # Check if household is vulnerable
        is_vulnerable = spm_unit("ny_liheap_vulnerable_household", period)
        
        # Check if household gets subsidized housing (no supplement for them)
        receives_housing_assistance = spm_unit(
            "receives_housing_assistance", period
        )
        
        # Only provide supplement if vulnerable and not in subsidized housing
        return where(
            is_vulnerable & ~receives_housing_assistance, 
            p.vulnerable_supplement, 
            0
        )