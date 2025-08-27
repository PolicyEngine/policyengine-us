from policyengine_us.model_api import *


class income_elasticity(Variable):
    value_type = float
    entity = Person
    label = "income elasticity of labor supply"
    unit = "/1"
    definition_period = YEAR
    adds = ["gov.simulation.labor_supply_responses.elasticities.income"]
