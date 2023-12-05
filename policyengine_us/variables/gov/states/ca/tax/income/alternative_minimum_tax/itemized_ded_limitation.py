from policyengine_us.model_api import *


class itemized_ded_limitation(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA itemized deductions limitation"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        itemized_ded_over_limitation = where(tax_unit("ca_agi", period) + tax_unit("ca_itemized_decutions", period) > p.itemized_ded_threshold[filing_status],
                                             tax_unit("ca_itemized_decutions", period), 0) 
        itemized_ded_limitation = where(tax_unit("ca_agi", period) < p.itemized_ded_threshold[filing_status],
                                 0, itemized_ded_over_limitation) 
        
        return itemized_ded_limitation