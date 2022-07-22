from openfisca_us.model_api import *
from openfisca_tools import homogenize_parameter_structures


class second_lowest_silver_plan_cost(Variable):
    value_type = float
    entity = TaxUnit
    label = "Second-lowest silver plan cost"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
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
        slspc = parameter_tree(
            period
        ).gov.hhs.medicaid.geography.second_lowest_silver_plan_cost
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
