from policyengine_us.model_api import *

class or_liheap_eligibility(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Oregon LIHEAP eligibility"
        definition_period = YEAR
        reference = "https://www.oregon.gov/ohcs/energy-weatherization/pages/utility-bill-payment-assistance.aspx"
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            income = tax_unit("adjusted_gross_income", period)  
            threshold = tax_unit("or_liheap_income_threshold", period)
            return income <= threshold
