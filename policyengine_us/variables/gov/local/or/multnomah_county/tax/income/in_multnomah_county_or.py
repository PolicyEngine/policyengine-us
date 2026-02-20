from policyengine_us.model_api import *


class in_multnomah_county_or(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "In Multnomah County, Oregon"
    reference = "https://multco.us/info/multnomah-county-preschool-all-personal-income-tax"

    def formula(household, period, parameters):
        county = household("county_str", period)
        return county == "MULTNOMAH_COUNTY_OR"
