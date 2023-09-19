from policyengine_us.model_api import *


class co_ccap_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap
        p_fpg = parameters(period).gov.hhs.fpg
        monthly_agi = np.round(tax_unit("adjusted_gross_income", period) / 12, 2)
        
        # Calculate monthly fpg limit
        county = tax_unit.household("county_str", period)
        hhs_fpg_rate = p.entry_threshold[county]
        size = tax_unit("tax_unit_size", period)
        hhs_fpg = p_fpg.first_person.CONTIGUOUS_US + (size-1) * p_fpg.additional_person.CONTIGUOUS_US
        monthly_hhs_fpg =  np.round(hhs_fpg * hhs_fpg_rate / 12, 2)
        
        # Calculate monthly smi limit
        spm_unit = tax_unit.spm_unit
        hhs_smi_rate = p.initial_income_eligibility
        hhs_smi = spm_unit("hhs_smi", period)
        monthly_hhs_smi = np.round(hhs_smi * hhs_smi_rate / 12, 2)

        return (monthly_agi < monthly_hhs_fpg) & (monthly_agi < monthly_hhs_smi)