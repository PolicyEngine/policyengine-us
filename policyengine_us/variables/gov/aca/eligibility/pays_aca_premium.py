from policyengine_us.model_api import *


class pays_aca_premium(Variable):
    value_type = bool
    entity = Person
    label = "Person pays an ACA marketplace premium"
    definition_period = YEAR
    reference = (
        # Marketplace enrollment itself has no income minimum.
        "https://www.law.cornell.edu/cfr/text/45/155.305#a",
        # The premium tax credit's income floor, and the below-poverty
        # exception for lawfully present immigrants.
        "https://www.law.cornell.edu/uscode/text/26/36B#c_1",
        # The credit's plans are those enrolled in through an Exchange
        # established by a State (36B(c)(2)(A)); "State" means the 50 States
        # and the District of Columbia (42 U.S.C. 18024(d)).
        "https://www.law.cornell.edu/uscode/text/26/36B#c_2_A",
        "https://www.law.cornell.edu/uscode/text/42/18024#d",
    )
    documentation = (
        "Whether a person is enrolled in a Marketplace plan and charged an "
        "age-rated premium for it. This is an enrollment test, not a pure "
        "status test: alongside the TIN, immigration-status, other-minimum-"
        "essential-coverage and age-based premium conditions, it excludes the "
        "Medicaid coverage gap, so it carries an income component, and it "
        "excludes Puerto Rico, Guam and the Virgin Islands, which have no "
        "Exchange. "
        "45 CFR 155.305(a) sets no income minimum for enrolling, so a person "
        "in the gap may buy a plan at full price; the model assumes none "
        "does, because the unsubsidized benchmark premium exceeds their "
        "income (policyengine-us #9472). A reader that wants the status and "
        "coverage conditions without that assumption should not reuse this "
        "variable."
    )

    def formula(person, period, parameters):
        immigration_eligible = person("is_aca_ptc_immigration_status_eligible", period)
        taxpayer_has_tin = person.tax_unit("taxpayer_has_tin", period)
        is_status_eligible = taxpayer_has_tin & immigration_eligible

        p = parameters(period).gov.aca
        is_coverage_eligible = add(person, period, p.ineligible_coverage) == 0
        is_aca_adult = person("age", period) > p.slcsp.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        pays_age_based_premium = is_aca_adult | child_pays

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

        # Puerto Rico, Guam and the Virgin Islands have no Exchange: 36B(c)(2)(A)
        # counts plans enrolled in through an Exchange established by a State,
        # and 42 U.S.C. 18024(d) defines a State as the 50 States and the
        # District of Columbia. So nobody in them is charged a Marketplace
        # premium.
        state_group = person.household("state_group", period)
        groups = state_group.possible_values
        has_exchange = (
            (state_group != groups.GU)
            & (state_group != groups.PR)
            & (state_group != groups.VI)
        )

        return (
            is_status_eligible
            & is_coverage_eligible
            & pays_age_based_premium
            & ~in_coverage_gap
            & has_exchange
        )
