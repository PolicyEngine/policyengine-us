from policyengine_us.model_api import *


class resolved_charitable_capital_gain_donations_50_pct(Variable):
    value_type = float
    entity = Person
    label = (
        "Resolved charitable capital gain property donations to 50% limit organizations"
    )
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170#b_1_C"
    documentation = (
        "Resolved person-level capital gain property donations to 50% limit organizations. "
        "When sub-box inputs are provided, they replace total donations. If both a total "
        "and both sub-boxes are set with the total larger, the sub-box inputs take precedence "
        "and any excess on the total is dropped."
    )

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
