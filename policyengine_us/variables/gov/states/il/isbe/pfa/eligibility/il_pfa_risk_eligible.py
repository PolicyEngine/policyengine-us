from policyengine_us.model_api import *


class il_pfa_risk_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Child meets risk factor requirements for Illinois PFA"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligible if: any highest priority factor OR 2+ risk factors.
        p = parameters(period).gov.states.il.isbe.pfa.eligibility.risk_factors
        highest_priority = person("il_pfa_highest_priority_eligible", period)
        risk_count = person("il_pfa_risk_factor_count", period)
        has_enough_risk_factors = risk_count >= p.minimum_required
        return highest_priority | has_enough_risk_factors
