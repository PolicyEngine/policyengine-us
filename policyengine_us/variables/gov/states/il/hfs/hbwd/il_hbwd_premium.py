from policyengine_us.model_api import *


class il_hbwd_premium(Variable):
    value_type = float
    entity = Person
    label = "Illinois Health Benefits for Workers with Disabilities monthly premium"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://hfs.illinois.gov/medicalprograms/hbwd/premiums.html",
        "https://ilga.gov/commission/jcar/admincode/089/089001200I05100R.html",
    )
    defined_for = "il_hbwd_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.il.hfs.hbwd.premium

        earned = person("il_hbwd_countable_earned_income", period)
        unearned = person("il_hbwd_countable_unearned_income", period)

        # Lookup premium components from bracket parameters
        earned_component = p.earned_component.calc(earned)
        unearned_component = p.unearned_component.calc(unearned)

        # Add components and apply $500 cap
        uncapped_premium = earned_component + unearned_component
        return min_(uncapped_premium, p.cap)
