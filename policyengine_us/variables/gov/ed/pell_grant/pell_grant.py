from policyengine_us.model_api import *


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
