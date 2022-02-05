from openfisca_us.model_api import *


class ca_cvrp(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "CVRP"
    unit = USD
    documentation = (
        "Total California Clean Vehicle Rebate Project (CVRP) benefit"
    )

    def formula(person, period, parameters):
        normal_eligible = person("is_ca_cvrp_normal_rebate_eligible")
        vehicle_amount = person("ca_cvrp_vehicle_rebate_amount", period)
        p_increased_amount = parameters(
            period
        ).states.ca.calepa.carb.cvrp.increased_rebate.amount
        increased_eligible = person("is_ca_cvrp_increased_rebate_eligible")
        bought_qualifying_ev = vehicle_amount > 0
        normal_amount = normal_eligible * vehicle_amount
        increased_amount = (
            increased_eligible & bought_qualifying_ev
        ) * p_increased_amount
        return normal_amount + increased_amount
