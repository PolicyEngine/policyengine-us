from policyengine_us.model_api import *


class il_pi_risk_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets risk factor requirements for Illinois PI"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/Prevention-Initiative-Eligibility-Form.pdf#page=3",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligible if priority score meets minimum (50 points).
        p = parameters(period).gov.states.il.isbe.pi.eligibility.risk_factors
        priority_score = person("il_pi_priority_score", period)
        return priority_score >= p.minimum_score
