from policyengine_us.model_api import *


class ny_liheap(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York State LIHEAP benefit amount"
    definition_period = YEAR
    defined_for = "ny_liheap_income_eligible"
    unit = USD
    reference = (
        "https://otda.ny.gov/programs/heap/",
        "https://otda.ny.gov/programs/heap/contacts/",
    )
    documentation = "Regular HEAP benefit amount for eligible households"
    
    def formula(spm_unit, period, parameters):
        # Calculate total benefit (base + supplement)
        base_benefit = spm_unit("ny_liheap_base_benefit", period)
        vulnerable_supplement = spm_unit("ny_liheap_vulnerable_supplement", period)
        total_benefit = base_benefit + vulnerable_supplement
        
        # Cap benefit at actual heating expenses
        heating_expense = spm_unit("heating_expense", period)
        
        # HEAP benefit cannot exceed actual heating costs
        return min_(total_benefit, heating_expense)