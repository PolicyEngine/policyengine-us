from policyengine_us.model_api import *


class pa_tanf_cahs_assistance_payout(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania TANF cash assistance payout"
    unit = USD
    definition_period = YEAR
    reference = (
        ""
    )
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.pa.dhs.tanf.cash_assistance
        county = spm_unit.household("county_str", period)
        #Group 1: Bucks, Chester, Lancaster, Montgomery, Pike
        bucks = county == "BUCKS_COUNTY_PA"
        chester = county == "CHESTER_COUNTY_PA"
        lancaster = county == "LANCASTER_COUNTY_PA"
        montgomery = county == "MONTGOMERY_COUNTY_PA"
        pike = county == "PIKE_COUNTY_PA"
        group_1 = [bucks, chester, lancaster, montgomery, pike]
        #Group 2:
        
        #Group 3:
        
        #Group 4:
        
        return 
