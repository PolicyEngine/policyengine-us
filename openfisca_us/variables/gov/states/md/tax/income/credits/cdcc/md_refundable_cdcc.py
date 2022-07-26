from openfisca_us.model_api import *


class md_refundable_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD refundable CDCC"
    documentation = "Maryland refundable Child and Dependent Care Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-716-for-child-care-or-dependent-care"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # Note: The MD refundable CDCC is based on the MD CDCC and MD tax before credits
        # *without respect to the other non-refundable credits* like MD EITC.
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)
        p = parameters(period).gov.states.md.tax.income.credits.cdcc
        cdcc = tax_unit("md_cdcc", period)
        # Refundable has its own AGI cap.
        cap = p.eligibility.refundable_agi_cap[filing_status]
        eligible = agi <= cap
        tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        return eligible * max_(0, cdcc - tax_before_credits)
