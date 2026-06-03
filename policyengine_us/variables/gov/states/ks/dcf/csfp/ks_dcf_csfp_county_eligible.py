from policyengine_us.model_api import *


KS_CSFP_COUNTIES = [
    # Kansas DCF's FAQ jurisdiction table and linked site spreadsheet
    # differ slightly, so include counties present in either DCF source.
    "ANDERSON_COUNTY_KS",
    "ATCHISON_COUNTY_KS",
    "BARBER_COUNTY_KS",
    "BARTON_COUNTY_KS",
    "BOURBON_COUNTY_KS",
    "BROWN_COUNTY_KS",
    "BUTLER_COUNTY_KS",
    "CHAUTAUQUA_COUNTY_KS",
    "CHEROKEE_COUNTY_KS",
    "CLAY_COUNTY_KS",
    "COWLEY_COUNTY_KS",
    "CRAWFORD_COUNTY_KS",
    "DECATUR_COUNTY_KS",
    "DONIPHAN_COUNTY_KS",
    "DOUGLAS_COUNTY_KS",
    "ELLIS_COUNTY_KS",
    "ELLSWORTH_COUNTY_KS",
    "FRANKLIN_COUNTY_KS",
    "GEARY_COUNTY_KS",
    "GRAHAM_COUNTY_KS",
    "GRANT_COUNTY_KS",
    "HARPER_COUNTY_KS",
    "HARVEY_COUNTY_KS",
    "HODGEMAN_COUNTY_KS",
    "JACKSON_COUNTY_KS",
    "JEFFERSON_COUNTY_KS",
    "JOHNSON_COUNTY_KS",
    "KEARNY_COUNTY_KS",
    "KINGMAN_COUNTY_KS",
    "KIOWA_COUNTY_KS",
    "LABETTE_COUNTY_KS",
    "LEAVENWORTH_COUNTY_KS",
    "LYON_COUNTY_KS",
    "MARION_COUNTY_KS",
    "MARSHALL_COUNTY_KS",
    "MIAMI_COUNTY_KS",
    "MITCHELL_COUNTY_KS",
    "MONTGOMERY_COUNTY_KS",
    "MORRIS_COUNTY_KS",
    "NEMAHA_COUNTY_KS",
    "OSAGE_COUNTY_KS",
    "OSBORNE_COUNTY_KS",
    "PAWNEE_COUNTY_KS",
    "PHILLIPS_COUNTY_KS",
    "POTTAWATOMIE_COUNTY_KS",
    "PRATT_COUNTY_KS",
    "RENO_COUNTY_KS",
    "RILEY_COUNTY_KS",
    "RUSSELL_COUNTY_KS",
    "SALINE_COUNTY_KS",
    "SEDGWICK_COUNTY_KS",
    "SEWARD_COUNTY_KS",
    "SHAWNEE_COUNTY_KS",
    "SHERMAN_COUNTY_KS",
    "STAFFORD_COUNTY_KS",
    "SUMNER_COUNTY_KS",
    "THOMAS_COUNTY_KS",
    "WABAUNSEE_COUNTY_KS",
    "WASHINGTON_COUNTY_KS",
    "WYANDOTTE_COUNTY_KS",
]


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
        return np.isin(county, KS_CSFP_COUNTIES)
