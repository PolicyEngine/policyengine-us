from policyengine_us.model_api import *


class il_pi_risk_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets risk factor requirements for Illinois PI"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/Documents/prevention-initiative-manual.pdf"
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligible if has at least minimum required risk factors.
        p = parameters(period).gov.states.il.isbe.pi.eligibility.risk_factors
        risk_count = person("il_pi_risk_factor_count", period)
        return risk_count >= p.minimum_required
