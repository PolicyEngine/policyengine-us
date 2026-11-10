from policyengine_us.model_api import *


class medicaid_ltss_special_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS special income limit"
    unit = USD
    definition_period = MONTH
    default_value = 0
    documentation = (
        "Special income limit for the applicant's modeled state and "
        "assistance unit, derived from the Supplemental Security Income "
        "federal benefit rate. Texas applies 300% of the individual rate, "
        "and twice that for a couple (1 TAC 358.433). Delaware applies 250% "
        "of the individual or couple rate (DSSM 20100.2.2). Washington "
        "applies 300% of the individual rate (WAC 182-513-1100); Washington "
        "couples and all other states are unmodeled and receive zero."
    )
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/435.1005",
        "https://www.law.cornell.edu/regulations/texas/1-Tex-Admin-Code-SS-358-433",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=1",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1100",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care.financial
        fbr = parameters(period).gov.ssa.ssi.amount
        state = person.household("state_code", period)
        states = state.possible_values
        assistance_unit_size = person("medicaid_ltss_assistance_unit_size", period)
        texas_individual_limit = p.tx.special_income_limit.rate * fbr.individual

        return select(
            [
                (state == states.TX) & (assistance_unit_size == 1),
                (state == states.TX) & (assistance_unit_size == 2),
                (state == states.DE) & (assistance_unit_size == 1),
                (state == states.DE) & (assistance_unit_size == 2),
                (state == states.WA) & (assistance_unit_size == 1),
            ],
            [
                texas_individual_limit,
                texas_individual_limit * p.tx.special_income_limit.couple_multiplier,
                p.de.special_income_limit.rate * fbr.individual,
                p.de.special_income_limit.rate * fbr.couple,
                p.wa.special_income_limit.rate * fbr.individual,
            ],
            default=0,
        )
