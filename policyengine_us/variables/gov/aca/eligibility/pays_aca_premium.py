from policyengine_us.model_api import *


class pays_aca_premium(Variable):
    value_type = bool
    entity = Person
    label = "Person pays an ACA marketplace premium"
    definition_period = YEAR

    def formula(person, period, parameters):
        immigration_eligible = person("is_aca_ptc_immigration_status_eligible", period)
        taxpayer_has_tin = person.tax_unit("taxpayer_has_tin", period)
        is_status_eligible = taxpayer_has_tin & immigration_eligible

        p = parameters(period).gov.aca
        is_coverage_eligible = add(person, period, p.ineligible_coverage) == 0
        is_aca_adult = person("age", period) > p.slcsp.max_child_age
        child_pays = person("aca_child_index", period) <= p.max_child_count
        pays_age_based_premium = is_aca_adult | child_pays

        # The coverage gap: under the premium tax credit's income floor with
        # no Medicaid pathway (a non-expansion state, or a status bar), and
        # without the below-poverty exception for lawfully present
        # immigrants, which 26 U.S.C. 36B(c)(1)(B) carried until P.L. 119-21
        # repealed it from 2026. Nobody in that gap buys the full-price
        # benchmark plan; charging it made a Wyoming adult at $0 of income
        # pay $11,769 a year (policyengine-us #9472). Only the floor is
        # gated: above the eligibility ceiling, where the 2026 subsidy cliff
        # returns, full price is what an enrollee pays.
        magi_frac = person.tax_unit("aca_magi_fraction", period)
        floor = p.ptc_income_eligibility.thresholds[1]
        below_fpl_exception = person.tax_unit(
            "aca_ptc_below_fpl_immigration_exception", period
        )
        in_coverage_gap = (magi_frac < floor) & ~below_fpl_exception

        return (
            is_status_eligible
            & is_coverage_eligible
            & pays_age_based_premium
            & ~in_coverage_gap
        )
