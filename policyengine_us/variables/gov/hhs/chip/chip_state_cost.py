from policyengine_us.model_api import *


class chip_state_cost(Variable):
    value_type = float
    entity = Person
    label = "CHIP state cost"
    documentation = (
        "Portion of CHIP expenditures borne by the state, equal to total "
        "CHIP cost less the federal share."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1397ee#b"
    defined_for = "chip_enrolled"

    def formula(person, period, parameters):
        cost = person("chip", period)
        federal_share = person("chip_federal_share", period)
        return cost * (1 - federal_share)
