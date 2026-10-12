from policyengine_us.model_api import *


class is_aca_marketplace_enrollee(Variable):
    value_type = bool
    entity = Person
    label = "Person is enrolled in Marketplace coverage"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/45/155.305#a",
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
    )
    documentation = (
        "Whether a person is enrolled in a Marketplace plan: the TIN, "
        "immigration-status, other-minimum-essential-coverage and Medicaid "
        "coverage-gap conditions of pays_aca_premium, without its premium "
        "condition. A child beyond the three oldest is enrolled but pays no "
        "age-rated premium (45 CFR 147.102(c)(1)); pays_aca_premium is this "
        "variable restricted to those who pay one."
    )

    def formula(person, period, parameters):
        immigration_eligible = person("is_aca_ptc_immigration_status_eligible", period)
        taxpayer_has_tin = person.tax_unit("taxpayer_has_tin", period)
        is_status_eligible = taxpayer_has_tin & immigration_eligible

        p = parameters(period).gov.aca
        is_coverage_eligible = add(person, period, p.ineligible_coverage) == 0

        # The Medicaid coverage gap: under the premium tax credit's income
        # floor, income-ineligible under the eligibility scale itself, with no
        # Medicaid pathway (already required by ineligible_coverage above: a
        # non-expansion state, or a status bar), and without the below-poverty
        # exception for lawfully present immigrants, which 26 U.S.C.
        # 36B(c)(1)(B) carried until P.L. 119-21 repealed it from 2026. The
        # scale's own result is read, not just its threshold, so a reform that
        # makes the first bracket income-eligible reopens the credit here
        # instead of being blocked by a threshold that did not move. The model
        # assumes nobody in that gap buys the full-price benchmark plan;
        # charging it made a Wyoming adult at $0 of income pay $11,769 a year
        # (policyengine-us #9472). Only the floor is gated: above the
        # eligibility ceiling, where the 2026 subsidy cliff returns, full
        # price is what an enrollee pays.
        income_eligibility = p.ptc_income_eligibility
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        floor = income_eligibility.thresholds[1]
        below_fpl_exception = person.tax_unit(
            "aca_ptc_below_fpl_immigration_exception", period
        )
        in_coverage_gap = (
            (magi_frac < floor)
            & ~income_eligibility.calc(magi_frac)
            & ~below_fpl_exception
        )

        return is_status_eligible & is_coverage_eligible & ~in_coverage_gap
