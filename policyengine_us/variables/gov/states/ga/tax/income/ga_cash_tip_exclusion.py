from policyengine_us.model_api import *


class ga_cash_tip_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia cash tip exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    # GA HB463 Section 2-4 adds O.C.G.A. § 48-7-27(a)(17).
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080#page=7"
    )

    def formula(tax_unit, period, parameters):
        # GA HB463 § 48-7-27(a)(17) (TY 2026-2028): each employee in a
        # customarily-tipped occupation may exclude up to $1,750 of cash
        # tips from Georgia taxable income.
        #
        # The bill defines "cash tips" to include cash plus charged tips
        # received voluntarily (but excludes mandatory service charges
        # where consequence-in-nonpayment, subject-to-negotiation, or
        # determined-by-payor fails). We approximate this with the generic
        # `tip_income` variable, which does not distinguish among cash,
        # charged, and mandatory categories. Reasonable approximation in
        # practice, since `tip_income` typically reflects voluntary tips.
        #
        # The bill defines "occupation that customarily and regularly
        # receives tips" by explicit reference to the federal Treasury
        # Tipped Occupation Code list and additionally excludes "occupations
        # excluded under Section 63 of the Internal Revenue Code." We use
        # `tip_income_deduction_occupation_requirement_met`, which checks
        # the Treasury list and excludes Specified Service Trades or
        # Businesses (via `~is_sstb`) — the IRC § 199A SSTB list is the
        # standard federal proxy for the occupation-exclusion clause.
        person = tax_unit.members
        tip_income = person("tip_income", period)
        occupation_eligible = person(
            "tip_income_deduction_occupation_requirement_met", period
        )
        qualified_tips = tip_income * occupation_eligible
        cap = parameters(period).gov.states.ga.tax.income.agi.exclusions.tips.cap
        return tax_unit.sum(min_(qualified_tips, cap))
