from policyengine_us.model_api import *


class nyc_school_tax_credit_rate_reduction_amount_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for NYC School Tax Credit Rate Reduction Amount"
    definition_period = YEAR
    defined_for = "in_nyc"
    reference = (
        # NY Tax Law § 606(ggg)(2), (4-b)
        "https://www.nysenate.gov/legislation/laws/TAX/606",
        "https://www.tax.ny.gov/pdf/2025/inc/it201i_2025.pdf#page=20",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.local.ny.nyc.tax.income.credits.school.rate_reduction
        # § 606(ggg)(4-b) denies the amount to any taxpayer with income over
        # the limit, where § 606(ggg)(2) defines income by reference to
        # RPTL § 425(4)(b)(ii) rather than city taxable income.
        income = tax_unit("nyc_school_credit_income", period)
        income_eligible = income <= p.income_limit
        # The (4-b) tables compute the amount on city taxable income and make
        # it not applicable above their top bracket.
        nyc_taxable_income = tax_unit("nyc_taxable_income", period)
        taxable_income_eligible = nyc_taxable_income <= p.taxable_income_limit
        return income_eligible & taxable_income_eligible
