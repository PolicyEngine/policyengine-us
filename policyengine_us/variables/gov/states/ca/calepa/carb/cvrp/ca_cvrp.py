from policyengine_us.model_api import *


class ca_cvrp(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "California Clean Vehicle Rebate Project"
    unit = USD
    documentation = (
        "Total California Clean Vehicle Rebate Project (CVRP) benefit"
    )
    reference = "https://cleanvehiclerebate.org/en/eligibility-guidelines"
    defined_for = StateCode.CA
    exhaustive_parameter_dependencies = "gov.states.ca.calepa.carb.cvrp"

    def formula(person, period, parameters):
        # Calculate normal rebate.
        normal_eligible = person("is_ca_cvrp_normal_rebate_eligible", period)
        vehicle_amount = person("ca_cvrp_vehicle_rebate_amount", period)
        normal_amount = normal_eligible * vehicle_amount
        # Calculate increased rebate (more means-tested).
        p_increased_amount = parameters(
            period
        ).gov.states.ca.calepa.carb.cvrp.increased_rebate.amount
        increased_eligible = person(
            "is_ca_cvrp_increased_rebate_eligible", period
        )
        bought_qualifying_ev = vehicle_amount > 0
        increased_amount = (
            increased_eligible & bought_qualifying_ev
        ) * p_increased_amount
        return normal_amount + increased_amount
