from policyengine_us.model_api import *

 class or_liheap_eligibility(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Oregon LIHEAP eligibility"
        definition_period = YEAR
        reference = "https://www.oregon.gov/ohcs/hcs-liheap.aspx"
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            income = tax_unit("tax_unit_income", period)  
            threshold = tax_unit("or_liheap_income_threshold", period)
            return income <= threshold
