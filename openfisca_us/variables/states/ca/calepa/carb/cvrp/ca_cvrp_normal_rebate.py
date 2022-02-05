from openfisca_us.model_api import *


class ca_cvrp_normal_rebate(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "CVRP normal rebate"
    unit = USD
    documentation = (
        "California Clean Vehicle Rebate Project (CVRP) normal rebate"
    )

    def formula(person, period, parameters):
        # AGI must be less than the threshold.
        agi = person.tax_unit("c00100", period)
        mars = person.tax_unit("mars", period)
        caps = parameters(period).states.ca.calepa.carb.cvrp.income_cap
        eligible = agi <= caps[mars]
        return eligible * person("ca_cvrp_vehicle_rebate_amount", period)
