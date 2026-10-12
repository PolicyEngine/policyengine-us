from policyengine_us.model_api import *


class ia_reportable_social_security(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa reportable social security benefits"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.iowa.gov/media/2650/download?inline#page=11",
        "https://revenue.iowa.gov/media/2721/download?inline#page=10",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        # The worksheet uses the head's and spouse's amounts from their federal
        # return; a tax unit dependent's benefits and interest are on the
        # dependent's own return.
        benefits = tax_unit_non_dep_add(tax_unit, period, ["social_security"])
        p = parameters(period).gov.states.ia.tax.income
        fraction = p.reportable_social_security.fraction
        # Worksheet line 7: one-half of the benefits (line 2), other income
        # (line 3, here AGI without taxable benefits, so already net of the
        # line 8 adjustments) and tax-exempt interest (line 6).
        income = (
            fraction * benefits
            + tax_unit("adjusted_gross_income", period)
            - add(tax_unit, period, ["taxable_social_security"])
            + tax_unit_non_dep_add(tax_unit, period, ["tax_exempt_interest_income"])
        )
        filing_status = tax_unit("filing_status", period)
        deduction = p.reportable_social_security.deduction[filing_status]
        return p.reportable_social_security.fraction * min_(
            benefits, max_(0, income - deduction)
        )
