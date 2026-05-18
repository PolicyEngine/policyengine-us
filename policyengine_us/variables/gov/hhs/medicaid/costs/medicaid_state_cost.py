from policyengine_us.model_api import *


class medicaid_state_cost(Variable):
    value_type = float
    entity = Person
    label = "Medicaid state cost"
    documentation = (
        "Portion of Medicaid expenditures borne by the state, equal to total "
        "Medicaid cost less the federal share."
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396b"
    defined_for = "medicaid_enrolled"

    def formula(person, period, parameters):
        cost = person("medicaid_cost", period)
        federal_share = person("medicaid_federal_share", period)
        return cost * (1 - federal_share)
