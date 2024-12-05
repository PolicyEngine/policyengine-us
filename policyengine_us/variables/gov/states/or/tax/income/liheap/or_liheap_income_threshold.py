from policyengine_us.model_api import *

class or_liheap_income_threshold(Variable):
        value_type = float
        entity = TaxUnit
        label = "Income threshold for Oregon LIHEAP eligibility"
        unit = USD
        definition_period = YEAR
        reference = "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"
        
        defined_for = StateCode.OR
        
        def formula(tax_unit, period, parameters):
            state_median_income = tax_unit("hhs_smi", period)  
            p = parameters(period).gov.states.["or"].liheap.eligibility
            return state_median_income * p.eligibility