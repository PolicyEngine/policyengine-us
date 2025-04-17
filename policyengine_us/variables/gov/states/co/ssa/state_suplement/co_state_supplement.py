from policyengine_us.model_api import *


class co_state_supplement(Variable):
    value_type = float
    entity = Person
    label = "Colorado State Supplement"
    definition_period = YEAR
    defined_for = "co_state_supplement_eligible"

    def formula(person, period, parameters):
        income = person("ssi_countable_income", period)
        both_eligible = person("ssi_marital_both_eligible", period)
        ssi = person("ssi", period)
        # The SSI variable assigns SSI to one member of the marital unit if both are eligible
        marital_ssi = where(
            both_eligible, person.marital_unit.sum(ssi) / 2, ssi
        )
        total_countable_income = marital_ssi + income
        p = parameters(period).gov.states.co.ssa.state_supplement
        grant_standard = p.grant_standard * MONTHS_IN_YEAR
        return max_(0, grant_standard - total_countable_income)
