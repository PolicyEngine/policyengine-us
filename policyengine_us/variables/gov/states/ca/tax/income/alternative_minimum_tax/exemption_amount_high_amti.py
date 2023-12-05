from policyengine_us.model_api import *


class exemption_amount_high_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA exemption amount for AMTI higher than threshold"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax
        
        exemption_amount_initial = p.exemption_amt[filing_status]
        amti = tax_unit("ca_amti", period)
        exemption_amount_low = p.exemption_amt_lower_threshold[filing_status]
        exemption_amount_high = max_(exemption_amount_initial - (amti - exemption_amount_low) * p.amti_rate, 0) # line 6
        
        #person = tax_unit.members
        #eligible_child = person("exemption_child_eligible", period) # how to calculate person in tax unit
        exemption_amount_child = p.exemption_amount_child
        earned_income = ""
        exemption_amount_child_total = exemption_amount_child + earned_income # line 9

        if eligible_child == True:
            return where(tax_unit("ca_amti", period) >= p.exemption_amt_upper_threshold[filing_status],
                                            0, min_(exemption_amount_high, exemption_amount_child_total))
        else:
            return where(tax_unit("ca_amti", period) >= p.exemption_amt_upper_threshold[filing_status],
                                            0, exemption_amount_high)