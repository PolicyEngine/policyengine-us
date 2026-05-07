from policyengine_us.model_api import *


class slcsp_rating_area_la_county(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area in Los Angeles County"
    definition_period = YEAR
    defined_for = "in_la"

    def formula(household, period, parameters):
        zip3 = household("three_digit_zip_code", period)
        p = parameters(period).gov.aca
        has_zip = zip3 != ""
        la_zip_params = p.la_county_rating_area
        valid_zips = set(la_zip_params._children.keys())
        is_known_zip = np.array([str(z) in valid_zips for z in zip3])
        can_lookup = has_zip & is_known_zip
        result = np.zeros(zip3.shape, dtype=int)
        if can_lookup.any():
            result[can_lookup] = la_zip_params[zip3[can_lookup]]
        return result
