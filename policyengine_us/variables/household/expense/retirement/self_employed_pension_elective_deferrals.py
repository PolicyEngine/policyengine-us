from policyengine_us.model_api import *


class self_employed_pension_elective_deferrals(Variable):
    value_type = float
    entity = Person
    label = "Self-employed plan elective deferrals"
    unit = USD
    documentation = (
        "Part of the person's own self-employed SEP, SIMPLE and qualified "
        "plan contributions (Schedule 1 line 16) that is elective deferrals "
        "under section 402(g)(3). Nonelective SEP and profit-sharing "
        "contributions, and the 401(k) or SIMPLE IRA matching contributions "
        "a self-employed person makes for themself (sections 402(g)(8) and "
        "408(p)(9)), are employer contributions, not elective deferrals. "
        "The line 16 deduction excludes designated Roth deferrals, so they "
        "are not modeled here. The modeled contribution does not say which "
        "plan the person has, so it counts as elective deferrals first, up "
        "to the section 402(g) limit plus the person's "
        "catch-up amount less their deferrals to other employers' 401(k) and "
        "403(b) plans; the rest are employer contributions. This is the most "
        "of the contributions that can be elective deferrals. For a SEP or a "
        "profit-sharing plan without a 401(k) arrangement, supply 0."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/402#g_1",
        "https://www.law.cornell.edu/uscode/text/26/402#g_3",
        "https://www.law.cornell.edu/uscode/text/26/402#g_8",
        "https://www.law.cornell.edu/uscode/text/26/408#p_9",
        "https://www.law.cornell.edu/uscode/text/26/414#v_3_A",
        "https://www.irs.gov/pub/irs-prior/f8880--2025.pdf#page=2",
        "https://www.irs.gov/pub/irs-prior/p590a--2025.pdf#page=47",
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=39",
    )

    def formula(person, period, parameters):
        contributions = person("self_employed_pension_contributions", period)
        # Section 402(g)(1) limits a person's elective deferrals across all
        # plans, so deferrals to other employers' plans use the room first.
        other_deferrals = add(
            person,
            period,
            [
                "traditional_401k_contributions",
                "roth_401k_contributions",
                "traditional_403b_contributions",
                "roth_403b_contributions",
            ],
        )
        deferral_room = max_(
            person("elective_deferral_limit", period) - other_deferrals, 0
        )
        return min_(contributions, deferral_room)
