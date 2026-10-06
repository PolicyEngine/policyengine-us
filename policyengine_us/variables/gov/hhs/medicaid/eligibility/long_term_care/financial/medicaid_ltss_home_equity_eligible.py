from policyengine_us.model_api import *


class medicaid_ltss_home_equity_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets Medicaid LTSS home-equity threshold"
    definition_period = MONTH
    documentation = (
        "Applies the 42 USC 1396p(f) substantial home equity payment bar "
        "from explicit home value, encumbrance, fractional-ownership, "
        "resident-exception, and hardship inputs. Washington elects the "
        "federal maximum limit (WAC 182-513-1350(8)(c)); Texas and Delaware "
        "apply the CPI-indexed federal minimum (TX Appendix XXXI; DSSM "
        "20320.7.B and 20320.7.E), which from 2028 cannot exceed the "
        "$1,000,000 non-agricultural maximum set by P.L. 119-21 section "
        "71108. Elections in other states are unmodeled: equity at or below "
        "the federal minimum passes, because no state may bar payment below "
        "that amount, and higher equity fails closed. This screen is not "
        "gated on the financial pathway because the payment bar applies to "
        "every long-term care applicant; the composite screen applies the "
        "pathway gate. A person with no equity interest always passes, and "
        "a resident spouse or child exception or a granted hardship waiver "
        "passes regardless of the equity amount or ownership share. The "
        "agricultural-land limit in the separate annual "
        "is_medicaid_long_term_care_home_equity_eligible chassis is not "
        "modeled here; that chassis applies the federal maximum in every "
        "state."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396p#f",
        "https://www.medicaid.gov/federal-policy-guidance/downloads/cib11182025.pdf#page=9",
        "https://fhb.hhs.texas.gov/sites/default/files/documents/mepd-26-2.pdf#page=465",
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/61c317a6-5b56-4745-83ff-60107295dd03#page=17",
        "https://app.leg.wa.gov/wac/default.aspx?cite=182-513-1350",
        "https://www.hca.wa.gov/assets/free-or-low-cost/income-standards-20260101.pdf#page=3",
    )

    def formula_2026_01_01(person, period, parameters):
        p = parameters(period).gov.hhs.medicaid.eligibility.long_term_care
        state = person.household("state_code", period)
        states = state.possible_values
        # The home-equity limits are annual (YEAR) parameters compared with a
        # stock of equity in a MONTH formula, so they are read as-is without
        # dividing by twelve.
        # From 2028, P.L. 119-21 section 71108 deems an indexed
        # non-agricultural amount above $1,000,000 equal to $1,000,000, so
        # the uprated federal minimum cannot exceed the federal maximum.
        home_equity_limit = where(
            state == states.WA,
            p.home_equity.limit,
            min_(p.home_equity.minimum_limit, p.home_equity.limit),
        )
        home_value = person("medicaid_ltss_home_market_value", period)
        encumbrances = person("medicaid_ltss_home_encumbrances", period)
        ownership_share = person("medicaid_ltss_home_ownership_share", period)
        valid_ownership_share = (ownership_share >= 0) & (ownership_share <= 1)
        applicant_home_equity = max_(home_value - encumbrances, 0) * ownership_share
        # 42 USC 1396p(f)(2) and (f)(4) make the payment bar inapplicable
        # regardless of the equity amount, so these exceptions do not depend
        # on a valid ownership share.
        exception = (
            add(
                person,
                period,
                [
                    "medicaid_ltss_home_occupied_by_spouse",
                    "medicaid_ltss_home_occupied_by_child_under_21",
                    "medicaid_ltss_home_occupied_by_blind_or_disabled_child",
                    "medicaid_ltss_home_equity_hardship_waiver",
                ],
            )
            > 0
        )

        return exception | (
            valid_ownership_share & (applicant_home_equity <= home_equity_limit)
        )
