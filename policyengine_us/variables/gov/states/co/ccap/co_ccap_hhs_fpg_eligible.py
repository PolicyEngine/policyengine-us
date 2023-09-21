from policyengine_us.model_api import *


class co_ccap_hhs_fpg_eligible(Variable):
    value_type = bool
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO
    
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap
        monthly_agi = np.round(tax_unit("adjusted_gross_income", period) / 12, 2)
        
        # Calculate monthly fpg limit
        county = tax_unit.household("county_str", period)
        hhs_fpg_rate = p.entry_fpg_rate[county]
        hhs_fpg = tax_unit("tax_unit_fpg", period)
        monthly_hhs_fpg =  np.round(hhs_fpg * hhs_fpg_rate / 12, 2)

        return monthly_agi < monthly_hhs_fpg