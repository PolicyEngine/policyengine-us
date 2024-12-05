from policyengine_us.model_api import *

class or_liheap_eligibility(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Oregon LIHEAP eligibility"
        definition_period = YEAR
        reference = "https://liheapch.acf.hhs.gov/profiles/Oregon.htm"
        defined_for = StateCode.ORu

        def formula(tax_unit, period, parameters):
            income = tax_unit("adjusted_gross_income", period)  
            threshold = tax_unit("or_liheap_income_threshold", period)
            return income <= threshold
