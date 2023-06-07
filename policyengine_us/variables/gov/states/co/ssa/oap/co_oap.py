from policyengine_us.model_api import *


class co_oap(Variable):
    value_type = float
    entity = Person
    label = "Colorado Old Age Pension"
    definition_period = YEAR
    defined_for = "co_oap_eligible"

    def formula(person, period, parameters):
        income = person("ssi_countable_income", period)
        ssi = person("ssi", period)
        total_countable_income = ssi + income
        p = parameters(period).gov.states.co.ssa.oap
        grant_standard = p.grant_standard * MONTHS_IN_YEAR
        return max_(0, grant_standard - total_countable_income)
