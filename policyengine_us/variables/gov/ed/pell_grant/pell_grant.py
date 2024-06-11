from policyengine_us.model_api import *
from policyengine_us.variables.gov.ed.pell_grant.sai.eligibility_type.pell_grant_eligibility_type import (
    PellGrantEligibilityType,
)


class pell_grant(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        coa = person("cost_of_attending_college", period)
        months_in_school = person("pell_grant_months_in_school", period)
        efc = person("pell_grant_efc", period)
        p = parameters(period).gov.ed.pell_grant
        unbounded = coa - efc
        capped = min_(unbounded, p.amount.max)
        amount = where(capped < p.amount.min, 0, capped)
        return amount * (months_in_school / p.months_in_school_year)

    def formula_2024(person, period, parameters):
        coa = person("cost_of_attending_college", period)
        sai = person("pell_grant_sai", period)
        eligibility = person("pell_grant_eligibility_type", period)
        p = parameters(period).gov.ed.pell_grant.amount
        unbound = coa - sai
        capped = min_(unbound, p.max)
        amount = where(capped < p.min, 0, capped)
        return select(
            [
                eligibility == PellGrantEligibilityType.INELIGIBLE,
                eligibility == PellGrantEligibilityType.MAXIMUM,
                eligibility == PellGrantEligibilityType.MINIMUM,
            ],
            [0, p.max, amount],
        )
