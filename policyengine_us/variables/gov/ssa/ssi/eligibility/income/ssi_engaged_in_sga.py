from policyengine_us.model_api import *


class ssi_engaged_in_sga(Variable):
    value_type = bool
    entity = Person
    label = "Income less than the SGA limit"
    definition_period = YEAR
    reference = "https://www.ssa.gov/OP_Home/cfr20/416/416-0971.htm"

    def formula(person, period, parameters):
        income = person("ssi_earned_income", period)
        monthly_income = income / MONTHS_IN_YEAR
        p = parameters(period).gov.ssa.sga

        # SGA does not apply to blind individuals
        is_blind = person("is_blind", period)

        return (monthly_income > p.non_blind) & ~is_blind
