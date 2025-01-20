from policyengine_us.model_api import *
from policyengine_core.parameters.operations import (
    homogenize_parameter_structures,
)
from policyengine_core.simulations import Simulation
from policyengine_us.parameters.gov.hhs.medicaid.geography import (
    second_lowest_silver_plan_cost as slspc_data,
)


class second_lowest_silver_plan_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest silver plan cost"
    unit = USD
    definition_period = YEAR
    hidden_input = True

    # Start with a new formula
    # 1. get the state code (state_code), age (age),
    # 2. Create a aca_rating_area place holder variable (no formula)
    # 3.

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        household = person.household
        state = household("state_code_str", period)

        # California special case (existing logic)
        if state == "CA":
            cofips = household("county_fips", period)
            LA_COUNTY_FIPS = 37
            in_la_county = cofips == LA_COUNTY_FIPS
            zip3 = household("aca_zip3_ca_county_la", period)
            return where(in_la_county, zip3, cofips)

        # Alaska and Massachusetts use ZIP3
        elif state in ["AK", "MA"]:
            return household("zip_3", period)

        # All other states use county FIPS
        else:
            return household("county_fips", period)


class aca_slspc_trimmed_age(Variable):
    value_type = int
    entity = Person
    label = "Age clipped to be in ACA SLSPC range"
    definition_period = YEAR

    def formula(person, period, parameters):
        age = person("age", period)
        p = parameters(period).gov.aca.slspc
        return max_(0, min_(64, age))


class person_aca_slspc(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost for person"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # Get state and rating area
        state = person.household("state_code_str", period)
        rating_area = person.tax_unit("aca_rating_area", period)

        # Get base cost for rating area
        base_costs = parameters(period).gov.aca.state_ratingarea_cost
        base_cost = base_costs[state][rating_area]

        # Get age and appropriate age curve
        age = person("aca_slspc_trimmed_age", period)
        age_curves = parameters(period).gov.aca.age_curves

        states_with_custom_curves = ["AL", "DC", "MA", "MN", "MS", "OR", "UT"]

        if state in states_with_custom_curves:
            age_curve = age_curves[state.lower()]
            if state == "DC":  # Handle DC's special file name
                age_curve = age_curves.district_of_columbia
        else:
            age_curve = age_curves.default

        age_factor = age_curve[age]

        # Calculate final cost
        return base_cost * age_factor


class aca_slspc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest ACA silver-plan cost for tax unit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        """Calculate the total SLSPC for the tax unit."""
        simulation = tax_unit.simulation

        # Check for user override
        if (
            simulation.get_holder("reported_slspc").get_array(period)
            is not None
        ):
            return simulation.calculate("reported_slspc", period)

        # Sum eligible person costs
        person_costs = tax_unit.members("person_aca_slspc", period)
        return tax_unit.sum(person_costs)

    # def formula(tax_unit, period, parameters):
    #     simulation: Simulation = tax_unit.simulation
    #     if (
    #         simulation.get_holder("reported_slspc").get_array(period)
    #         is not None
    #     ):
    #         # If the user has provided a value for the second-lowest silver plan
    #         # cost, use that.
    #         return simulation.calculate("reported_slspc", period)
    #     person = tax_unit.members
    #     household = person.household
    #     area = household("medicaid_rating_area", period)
    #     state = household("state_code_str", period)
    #     age = person("age", period)
    #     age_code = select(
    #         [
    #             age < 21,
    #             age < 64,
    #             age >= 64,
    #         ],
    #         [
    #             "0-20",
    #             age.astype(int).astype(str),
    #             "64+",
    #         ],
    #     )
    #     eligible = person.tax_unit("is_ptc_eligible", period)
    #     per_person_cost = np.zeros_like(age)
    #     lookup_df = pd.DataFrame(
    #         {
    #             "state": state,
    #             "rating_area": area,
    #             "age": age_code,
    #         }
    #     )
    #     merged = pd.merge(
    #         lookup_df[eligible],
    #         slspc_data,
    #         how="left",
    #         on=["state", "rating_area", "age"],
    #     ).value.values
    #     per_person_cost = np.zeros_like(age)
    #     per_person_cost[eligible] = merged
    #     return tax_unit.sum(per_person_cost)
