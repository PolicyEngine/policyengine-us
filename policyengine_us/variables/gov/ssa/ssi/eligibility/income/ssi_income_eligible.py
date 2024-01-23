from policyengine_us.model_api import *


class ssi_income_eligible(Variable):
    value_type = float
    entity = Person
    label = "Income less than the SGA limit"
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        income = person("ssi_earned_income", period)
        monthly_income = income / MONTHS_IN_YEAR
        sga = parameters(period).gov.ssa.ssi.income.limit.sga

        # SGA does not apply to blind individuals
        is_blind = person("is_blind", period)

        return (monthly_income < sga) | is_blind
