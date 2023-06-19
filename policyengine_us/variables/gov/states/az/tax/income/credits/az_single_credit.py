from policyengine_us.model_api import *


class az_single_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "AZ single credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period) 
        single = filing_status == filing_status.possible_values.SINGLE

        phase_in_max_income = p.eligibility.single
        eligible = income <= phase_in_max_income
        
        return min_(p.amount*single*eligible, 120)
