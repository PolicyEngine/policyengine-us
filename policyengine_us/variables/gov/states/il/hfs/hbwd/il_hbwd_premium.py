from policyengine_us.model_api import *


class il_hbwd_premium(Variable):
    value_type = float
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities monthly premium"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/hbwd/premiums.html",
        "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-120.510",
    )
    defined_for = "il_hbwd_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.premium

        earned = person("il_hbwd_countable_earned_income", period)
        unearned = person("il_hbwd_countable_unearned_income", period)

        # Lookup premium components from bracket parameters
        return p.earned.calc(earned) + p.unearned.calc(unearned)
