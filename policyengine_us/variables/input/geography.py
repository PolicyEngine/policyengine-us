from policyengine_us.model_api import *
from policyengine_core.parameters import homogenize_parameter_structures
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.state_name import (
    StateName,
)
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    medicaid_rating_areas,
    second_lowest_silver_plan_cost,
)

label = "Geography"


class state_name(Variable):
    value_type = Enum
    possible_values = StateName
    default_value = StateName.CA
    entity = Household
    label = "State"
    definition_period = YEAR

    def formula(household, period, parameters):
        fips = household("state_fips", period)
        return (
            pd.Series(fips)
            .map(
                {
                    1: StateName.AL,
                    2: StateName.AK,
                    4: StateName.AZ,
                    5: StateName.AR,
                    6: StateName.CA,
                    8: StateName.CO,
                    9: StateName.CT,
                    10: StateName.DE,
                    11: StateName.DC,
                    12: StateName.FL,
                    13: StateName.GA,
                    15: StateName.HI,
                    16: StateName.ID,
                    17: StateName.IL,
                    18: StateName.IN,
                    19: StateName.IA,
                    20: StateName.KS,
                    21: StateName.KY,
                    22: StateName.LA,
                    23: StateName.ME,
                    24: StateName.MD,
                    25: StateName.MA,
                    26: StateName.MI,
                    27: StateName.MN,
                    28: StateName.MS,
                    29: StateName.MO,
                    30: StateName.MT,
                    31: StateName.NE,
                    32: StateName.NV,
                    33: StateName.NH,
                    34: StateName.NJ,
                    35: StateName.NM,
                    36: StateName.NY,
                    37: StateName.NC,
                    38: StateName.ND,
                    39: StateName.OH,
                    40: StateName.OK,
                    41: StateName.OR,
                    42: StateName.PA,
                    44: StateName.RI,
                    45: StateName.SC,
                    46: StateName.SD,
                    47: StateName.TN,
                    48: StateName.TX,
                    49: StateName.UT,
                    50: StateName.VT,
                    51: StateName.VA,
                    53: StateName.WA,
                    54: StateName.WV,
                    55: StateName.WI,
                    56: StateName.WY,
                    72: StateName.PR,
                }
            )
            .values
        )


class medicaid_rating_area(Variable):
    value_type = int
    entity = Household
    label = "Medicaid rating area"
    definition_period = YEAR
    hidden_input = True

    def formula(household, period, parameters):
        simulation: Simulation = household.simulation
        if (
            simulation.get_holder("reported_slspc").get_array(period)
            is not None
        ):
            # If the user has provided a value for the second-lowest silver plan
            # cost, skip.
            return 0

        three_digit_zip_code = household("three_digit_zip_code", period)
        county = household("county_str", period)
        # Try a lookup on zip code, fill missing values with a lookup on county, fill missing with zero.
        df = pd.DataFrame(
            {
                "location": county,
            }
        )
        df_matched = pd.merge(
            df,
            medicaid_rating_areas,
            how="left",
            left_on="location",
            right_on="location",
        )
        county_lookup_failed = df_matched.rating_area.isna()
        df_matched.location[county_lookup_failed] = three_digit_zip_code[
            county_lookup_failed
        ]
        df_matched = pd.merge(
            df_matched,
            medicaid_rating_areas,
            how="left",
            left_on="location",
            right_on="location",
        )
        df_matched["rating_area"] = df_matched["rating_area_x"].fillna(
            df_matched["rating_area_y"]
        )
        return df_matched["rating_area"].fillna(1)


class reported_slspc(Variable):
    value_type = float
    entity = TaxUnit
    label = "reported second lowest silver plan cost"
    unit = USD
    definition_period = YEAR
    hidden_input = True


class county_fips(Variable):
    value_type = int
    label = "County FIPS code"
    entity = Household
    definition_period = YEAR
    documentation = "County FIPS code"


class state_fips(Variable):
    value_type = int
    label = "State FIPS code"
    entity = Household
    definition_period = YEAR
    documentation = "State FIPS code"
    default_value = 6
