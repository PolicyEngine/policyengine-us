from policyengine_us.model_api import *


class pell_grant_sai(Variable):
    value_type = float
    entity = Person
    unit = USD
    definition_period = YEAR
    label = "Pell Grant student aid index"

    def formula(person, period, parameters):
        head_contribution = person("pell_grant_head_contribution", period)
        dependent_contribution = person(
            "pell_grant_dependent_contribution", period
        )
        formula = person("pell_grant_formula", period)
        eligibility_type = person("pell_grant_eligibility_type", period)
        max_eligible = (
            eligibility_type == eligibility_type.possible_values.MAXIMUM
        )
        p = parameters(period).gov.ed.pell_grant.sai
        min_sai = p.limits.min_sai
        max_sai = where(max_eligible, 0, p.limits.max_sai)

        dependent_contribution_applies = formula == formula.possible_values.A
        applicable_dependent_contribution = (
            dependent_contribution_applies * dependent_contribution
        )
        unbound = head_contribution + applicable_dependent_contribution

        bound_ssi = min_(unbound, max_sai)
        return max_(bound_ssi, min_sai)
