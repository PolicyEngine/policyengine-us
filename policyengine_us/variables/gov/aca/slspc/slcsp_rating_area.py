from policyengine_us.model_api import *


class slcsp_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Second-lowest ACA silver-plan cost rating area"
    definition_period = YEAR

    def formula(household, period, parameters):
        # For LA County households, try the zip-code-specific lookup first.
        # That lookup returns 0 when the three_digit_zip_code is missing
        # (e.g., CPS records) or unmapped, in which case we fall back to the
        # county-level aca_rating_areas.csv mapping so LA still gets a valid
        # rating area (16) rather than an unknown (0) that zeros out slcsp.
        default_rating_area = household("slcsp_rating_area_default", period)
        la_rating_area = household("slcsp_rating_area_la_county", period)
        return where(
            household("in_la", period),
            where(la_rating_area == 0, default_rating_area, la_rating_area),
            default_rating_area,
        )
