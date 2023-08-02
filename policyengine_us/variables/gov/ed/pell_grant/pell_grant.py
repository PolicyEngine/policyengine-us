from policyengine_us.model_api import *


class pell_grant(Variable):
    value_type = float
    entity = Person
    label = "Pell Grant amount"
    documentation = "SPM unit's Pell Grant educational subsidy"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        coa = person("pell_grant_cost_of_attendance", period)
        months_in_school = person("pell_grant_months_in_school", period)
        efc = person("pell_grant_efc", period)
        p = parameters(period).gov.ed.pell_grant
        minimum = p.min_grant
        maximum = p.max_grant
        amount = min_(coa - efc, maximum)
        amount = where(amount < minimum, 0, amount)
        return amount * (months_in_school / p.months_in_school_year)
