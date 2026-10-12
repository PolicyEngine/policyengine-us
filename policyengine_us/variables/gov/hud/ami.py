from policyengine_us.model_api import *
from policyengine_us.parameters.gov.hud.income_limits import lookup_income_limit


class ami(Variable):
    value_type = float
    entity = Household
    label = "Area median income"
    documentation = "Area median income for a four-person household"
    definition_period = YEAR

    def formula(household, period, parameters):
        county_fips = household("county_fips", period)
        return lookup_income_limit(
            county_fips,
            period.start.year,
            "ami",
        )
