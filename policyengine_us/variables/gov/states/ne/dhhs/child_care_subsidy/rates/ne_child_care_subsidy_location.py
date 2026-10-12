from policyengine_us.model_api import *


class NEChildCareSubsidyLocation(Enum):
    URBAN = "Urban"
    RURAL = "Rural"


class ne_child_care_subsidy_location(Variable):
    value_type = Enum
    entity = Household
    possible_values = NEChildCareSubsidyLocation
    default_value = NEChildCareSubsidyLocation.RURAL
    definition_period = YEAR
    label = "Nebraska Child Care Subsidy rate location"
    defined_for = StateCode.NE
    reference = ("https://dhhs.ne.gov/Child%20Care%20Documents/Subsidy-Rates.pdf",)

    def formula(household, period, parameters):
        p = parameters(period).gov.states.ne.dhhs.child_care_subsidy.provider
        county = household("county_str", period)
        return where(
            np.isin(county, p.urban_counties),
            NEChildCareSubsidyLocation.URBAN,
            NEChildCareSubsidyLocation.RURAL,
        )
