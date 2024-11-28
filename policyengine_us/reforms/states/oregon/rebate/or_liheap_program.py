from policyengine_us.model_api import *

def create_or_liheap_program() -> Reform:
    class or_liheap_income_threshold(Variable):
        value_type = float
        entity = TaxUnit
        label = "Income threshold for Oregon LIHEAP eligibility"
        unit = USD
        definition_period = YEAR
        reference = "https://www.oregon.gov/ohcs/hcs-liheap.aspx"
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            state_median_income = tax_unit("hhs_smi", period)  
            p = parameters(period).gov.states.["or"].liheap.eligibility
            return state_median_income * p.eligibility

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

