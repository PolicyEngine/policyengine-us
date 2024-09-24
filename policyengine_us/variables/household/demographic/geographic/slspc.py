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

    def formula(tax_unit, period, parameters):
        simulation: Simulation = tax_unit.simulation
        if (
            simulation.get_holder("reported_slspc").get_array(period)
            is not None
        ):
            # If the user has provided a value for the second-lowest silver plan
            # cost, use that.
            return simulation.calculate("reported_slspc", period)
        person = tax_unit.members
        household = person.household
        area = household("medicaid_rating_area", period)
        state = household("state_code_str", period)
        age = person("age", period)
        age_code = select(
            [
                age < 21,
                age < 64,
                age >= 64,
            ],
            [
                "0-20",
                age.astype(int).astype(str),
                "64+",
            ],
        )
        eligible = person.tax_unit("is_ptc_eligible", period)
        per_person_cost = np.zeros_like(age)
        lookup_df = pd.DataFrame(
            {
                "state": state,
                "rating_area": area,
                "age": age_code,
            }
        )
        merged = pd.merge(
            lookup_df[eligible],
            slspc_data,
            how="left",
            on=["state", "rating_area", "age"],
        ).value.values
        per_person_cost = np.zeros_like(age)
        per_person_cost[eligible] = merged
        return tax_unit.sum(per_person_cost)
