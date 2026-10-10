from policyengine_us.model_api import *


class ga_surplus_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia surplus tax rebate"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legis.ga.gov/api/legislation/document/20232024/217823",
        "https://www.legis.ga.gov/api/legislation/document/20232024/217823#page=2",
    )
    defined_for = StateCode.GA
    # Not modeled: the statutory eligibility conditions in O.C.G.A.
    # 48-7-20.2(a)-(b) - filing both 2021 and 2022 returns ((a), (b)(1)),
    # the nonresident-alien exclusion ((a)(1)(A)), the estate or trust
    # exclusion ((a)(1)(C)), and part-year/nonresident proration ((b)(2)) -
    # are all treated as met for a full-year Georgia tax unit.

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ga.tax.income.credits.surplus_tax_rebate
        cap = p.amount[filing_status]
        # 48-7-20.2(b)(1)(A): capped at the Form 500 Line 16 liability (tax
        # before credits); it pays out past a zero balance due.
        line_16_tax = tax_unit("ga_income_tax_before_non_refundable_credits", period)
        # 48-7-20.2(a)(1)(B) and (a)(2): an individual claimed as a dependent
        # for 2021 is a qualified taxpayer only if that individual had 2021
        # earned income. The refund is credited to a qualified taxpayer, so a
        # joint return gets the joint amount while either spouse qualifies.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        own_earnings = person("earned_income", period) > 0
        qualified = tax_unit.any(filer & (~claimed | own_earnings))
        return min_(cap, line_16_tax) * qualified
