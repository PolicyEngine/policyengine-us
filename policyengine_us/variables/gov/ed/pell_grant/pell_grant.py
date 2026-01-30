from policyengine_us.model_api import *


class pell_grant(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        coa = person("cost_of_attending_college", period)
        p = parameters(period).gov.ed.pell_grant

        if p.uses_sai:
            sai = person("pell_grant_sai", period)
            eligibility = person("pell_grant_eligibility_type", period)
            unbounded = coa - sai
            amount = where(unbounded < p.amount.min, 0, unbounded)
            uncapped = select(
                [
                    eligibility == eligibility.possible_values.MAXIMUM,
                    eligibility == eligibility.possible_values.MINIMUM,
                ],
                [p.amount.max, amount],
                default=0,
            )
        else:
            months_in_school = person("pell_grant_months_in_school", period)
            efc = person("pell_grant_efc", period)
            unbounded = coa - efc
            amount = where(unbounded < p.amount.min, 0, unbounded)
            uncapped = amount * (months_in_school / p.months_in_school_year)

        max_amount = min_(coa, p.amount.max)
        return min_(max_amount, uncapped)
