from policyengine_us.model_api import *
from policyengine_core.parameters.operations import (
    homogenize_parameter_structures,
)
from policyengine_core.simulations import Simulation


class second_lowest_silver_plan_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest silver plan cost"
    unit = USD
    definition_period = YEAR
    defined_for = "is_ptc_eligible"
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
        parameter_tree = tax_unit.simulation.tax_benefit_system.parameters
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
                tax_unit.simulation.tax_benefit_system.variables,
            )
            parameter_tree.gov.hhs.medicaid.add_child(
                "geography", medicaid_parameters
            )
        person = tax_unit.members
        household = person.household
        area = household("medicaid_rating_area", period)
        state = household("state_code_str", period)
        age = person("age", period)
        slspc = parameter_tree.gov.hhs.medicaid.geography.second_lowest_silver_plan_cost(
            period
        )
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
        per_person_cost = index_(
            into=slspc,
            indices=[state, area, age_code],
            where=eligible,
        )
        return tax_unit.sum(per_person_cost)
