from policyengine_us.model_api import *


class taxable_income_plus_section_911_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Taxable income plus the section 911 exclusion"
    unit = USD
    documentation = (
        "Taxable income increased by the foreign earned income and housing "
        "amounts excluded under 26 U.S.C. 911(a). The regular tax of a "
        "taxpayer excluding foreign earned income is the tax on this amount "
        "less the tax on the excluded amount alone. Line 3 of the Foreign "
        "Earned Income Tax Worksheet; equals taxable income for everyone else."
    )
    definition_period = YEAR
    reference = [
        dict(
            title="26 U.S. Code § 911(f)(1)(A)(i)",
            href="https://www.law.cornell.edu/uscode/text/26/911#f_1_A_i",
        ),
        dict(
            title="2025 Form 1040 instructions, Foreign Earned Income Tax Worksheet—Line 16, line 3",
            href="https://www.irs.gov/pub/irs-pdf/i1040gi.pdf#page=37",
        ),
    ]

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        # Worksheet line 2c: "If zero or less, enter -0-".
        excluded = max_(0, tax_unit("foreign_earned_income_exclusion", period))
        return taxable_income + excluded
