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
        ELEMENTS = ["ca_cvrp_normal_rebate", "ca_cvrp_increased_rebate"]
        return add(person, period, ELEMENTS)
