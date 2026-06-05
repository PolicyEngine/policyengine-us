from policyengine_us.model_api import *


class mo_dhss_csfp_county_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Missouri DHSS CSFP county eligible"
    defined_for = StateCode.MO
    reference = (
        "https://health.mo.gov/living/wellness/nutrition/foodprograms/csfp/",
        "https://health.mo.gov/living/wellness/nutrition/foodprograms/csfp/pdf/missouri-state-plan-ada.pdf",
        "https://www.arcgis.com/home/item.html?id=d8d8553132194b2ebd038d171503e16c",
        "https://gis.mo.gov/arcgis/rest/services/DHSS/commodityFood/MapServer/0",
    )

    def formula(household, period, parameters):
        county = household("county_str", period)
        p = parameters(period).gov.states.mo.dhss.csfp
        if len(p.counties) == 0:
            return np.ones_like(county, dtype=bool)
        return np.isin(county, p.counties)
