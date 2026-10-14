from policyengine_us.model_api import *


class charitable_capital_gain_donations_50_pct(Variable):
    value_type = float
    entity = Person
    label = "Charitable capital gain property donations to 50% limit organizations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_C"

    def formula(person, period, parameters):
        cg_50_explicit = person("charitable_capital_gain_donations_50_pct_orgs", period)
        cg_to_non_50 = person(
            "charitable_capital_gain_donations_non_50_pct_orgs", period
        )
        cg_total = person("charitable_capital_gain_donations", period)
        return where(
            cg_50_explicit > 0,
            cg_50_explicit,
            max_(0, cg_total - cg_to_non_50),
        )
