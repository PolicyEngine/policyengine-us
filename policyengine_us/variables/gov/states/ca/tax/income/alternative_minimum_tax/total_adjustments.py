from policyengine_us.model_api import *


class total_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA total adjustments and preferences for AMTI calculation"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax
        
        total_adjustments = where(tax_unit("ca_itemized_deductions", period) > 0, 
                                  add(tax_unit, period, p.amti_sources) - tax_unit("ca_standard_deductions", period), # if itemized, line 1 = 0
                                  add(tax_unit, period, p.amti_sources) # if not itemized, sum up line 1-6 
        )

        return total_adjustments
        
         