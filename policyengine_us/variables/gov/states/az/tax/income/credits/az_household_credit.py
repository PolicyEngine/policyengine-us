from policyengine_us.model_api import *


class az_household_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "AZ single household credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period) 
        household = filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD

        dependent = tax_unit("tax_unit_dependents", period)
        spouse = tax_unit("is_tax_unit_household", period)
        adult = tax_unit("num", period)


        phase_in_max_income = p.eligibility.household.calc(dependent)
        eligible = income <= phase_in_max_income
        
        return min_(p.amount*(dependent + adult)*household*~spouse*eligible, 240)
