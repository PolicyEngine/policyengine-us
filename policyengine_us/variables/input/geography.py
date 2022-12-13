from policyengine_us.model_api import *
from policyengine_core.parameters import homogenize_parameter_structures
from policyengine_core.simulations import Simulation
from policyengine_us.variables.household.demographic.geographic.state_name import (
    StateName,
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
        fips = household("fips", period)
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
        parameter_tree = household.simulation.tax_benefit_system.parameters
        if not hasattr(parameter_tree.gov.hhs.medicaid, "geography"):
            medicaid_parameters = ParameterNode(
                directory_path=REPO
                / "data"
                / "parameters"
                / "gov"
                / "hhs"
                / "medicaid"
                / "geography"
            )
            medicaid_parameters = homogenize_parameter_structures(
                medicaid_parameters,
                household.simulation.tax_benefit_system.variables,
            )
            parameter_tree.gov.hhs.medicaid.add_child(
                "geography", medicaid_parameters
            )
        mra = parameter_tree(
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


class reported_slspc(Variable):
    value_type = float
    entity = TaxUnit
    label = "reported second lowest silver plan cost"
    unit = USD
    definition_period = YEAR
    hidden_input = True
