from policyengine_us.model_api import *


class charitable_cash_donations_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Charitable cash donations to 50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_A"

    def formula(person, period, parameters):
        cash_50_explicit = person("charitable_cash_donations_50_pct_orgs", period)
        cash_to_non_50 = person("charitable_cash_donations_non_50_pct_orgs", period)
        cash_total = person("charitable_cash_donations", period)
        return where(
            cash_50_explicit > 0,
            cash_50_explicit,
            max_(0, cash_total - cash_to_non_50),
        )
