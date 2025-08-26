from policyengine_us.model_api import *


class id_liheap_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Idaho LIHEAP"
    definition_period = YEAR
    reference = (
        "https://healthandwelfare.idaho.gov/services-programs/financial-assistance/home-heating-and-utility-assistance/",
        "https://www.eicap.org/our-programs/family-services/energy-assistance-winter-heating-program/"
    )
    documentation = "Determines eligibility for Idaho Low Income Home Energy Assistance Program"

    def formula(person, period, parameters):
        # Check if person lives in Idaho
        state_code = person.household("state_code_str", period)
        is_idaho_resident = state_code == "ID"
        
        # Get income and income limit
        spm_unit = person.spm_unit
        household_income = spm_unit("id_liheap_income", period)
        income_limit = person("id_liheap_income_limit", period)
        
        # Check if income is under limit
        income_eligible = household_income <= income_limit
        
        # Check SNAP presumptive eligibility
        snap_eligible = spm_unit("id_liheap_snap_eligible", period)
        
        # Eligible if:
        # 1. Lives in Idaho AND
        # 2. Either income eligible OR SNAP recipient
        return is_idaho_resident & (income_eligible | snap_eligible)