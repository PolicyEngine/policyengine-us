from policyengine_us.model_api import *


class tob_revenue_total(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Total trust fund revenue from SS benefit taxation"
    documentation = (
        "Increase in chapter 1 income tax liability after nonrefundable "
        "credits and before refundable credits from taxing Social Security "
        "benefits, per 42 U.S.C. 401 note. Excludes chapter 2A net investment "
        "income tax under section 1411. The total and its "
        "OASDI and Medicare HI shares are signed: negative unit differences "
        "are retained for aggregation."
    )
    unit = USD
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/401",
        "https://www.law.cornell.edu/uscode/text/26/1411",
    )

    def formula(tax_unit, period, parameters):
        """
        Calculate total trust fund revenue using branching + neutralization.

        This isolates the chapter 1 tax impact of including taxable SS in AGI
        by comparing chapter 1 liability with and without taxable SS.
        """
        # Chapter 1 liability WITH taxable SS, in the current state
        income_tax_with_ss = tax_unit("income_tax_chapter_1", period)
        # Cached on the parent after its branch is released
        income_tax_without_ss = tax_unit("income_tax_without_social_security", period)

        return income_tax_with_ss - income_tax_without_ss
