from openfisca_us.model_api import *


class medicaid_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Medicaid rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        mra = parameters(
            period
        ).gov.hhs.medicaid.geography.medicaid_rating_area
        three_digit_zip_code = household("three_digit_zip_code", period)
        county = household("county_str", period)
        locations = np.array(list(mra._children))
        county_in_locations = np.isin(county, locations)
        location = where(
            county_in_locations,
            county,
            three_digit_zip_code,
        )
        valid_location = np.isin(location, locations)
        rating_areas = np.ones_like(
            location
        )  # ~2.8% of locations don't match with a a scraped MRA. For these, we assign to the State's first MRA.
        if valid_location.sum() > 0:
            rating_areas[valid_location] = mra[location[valid_location]]
        return rating_areas
