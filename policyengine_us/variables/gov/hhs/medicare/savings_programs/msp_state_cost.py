from policyengine_us.model_api import *


class msp_state_cost(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program state cost"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396b",
        "https://www.law.cornell.edu/uscode/text/42/1396d#b",
        "https://www.law.cornell.edu/uscode/text/42/1396u-3#d",
    )
    documentation = "State share of limited-benefit Medicare Savings Program cost."

    def formula(person, period, parameters):
        return max_(
            person("msp_cost", period) - person("msp_federal_cost", period),
            0,
        )
