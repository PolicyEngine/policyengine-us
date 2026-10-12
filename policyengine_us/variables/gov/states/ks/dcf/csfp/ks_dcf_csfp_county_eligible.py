from policyengine_us.model_api import *


class ks_dcf_csfp_county_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Kansas DCF CSFP county eligible"
    defined_for = StateCode.KS
    reference = (
        "https://www.dcf.ks.gov/services/ees/pages/usda-commodity-programs/csfp/csfp-faqs.aspx",
        "https://content.dcf.ks.gov/ees/KEESM/Intranet/CSFPSitesbyJurisdiction.xlsx",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.ks.dcf.csfp
        return np.isin(county, p.counties)
