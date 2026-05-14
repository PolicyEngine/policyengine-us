from policyengine_us.model_api import *


class ga_cash_tip_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia cash tip exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20252026/249080",  # GA HB463 Section 2-4 adding O.C.G.A. 48-7-27(a)(17)
    )

    def formula(tax_unit, period, parameters):
        # GA HB463 Section 2-4 paragraph (17): for tax years 2026-2028, each
        # employee in a customarily-tipped occupation may exclude up to $1,750
        # of cash tips from Georgia taxable income. The occupation requirement
        # mirrors the federal Treasury Tipped Occupation Code list.
        person = tax_unit.members
        tip_income = person("tip_income", period)
        occupation_eligible = person(
            "tip_income_deduction_occupation_requirement_met", period
        )
        qualified_tips = tip_income * occupation_eligible
        cap = parameters(period).gov.states.ga.tax.income.agi.exclusions.tips.cap
        capped = min_(qualified_tips, cap)
        return tax_unit.sum(capped)
