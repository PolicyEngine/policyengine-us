from policyengine_us.model_api import *


class amt_income_less_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax Income less exemptions"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) income less exemptions"
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/55#b_1_B",
        "https://www.law.cornell.edu/uscode/text/26/55#d_4_A_iii",
        "https://www.irs.gov/pub/irs-pdf/i6251.pdf#page=9",
    ]

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.income.amt
        # Form 6251, Part I
        # Line 4
        amt_income = tax_unit("amt_income", period)
        if p.exemption.child.in_effect:
            # For filers subject to the kiddie tax, the deductions are not
            # added back
            taxable_income = tax_unit("taxable_income", period)
            kiddie_tax_applies = tax_unit("amt_kiddie_tax_applies", period)
            applied_income = where(kiddie_tax_applies, taxable_income, amt_income)
        else:
            # IRC 55(d)(4)(A)(iii) turns off the child limitation for taxable
            # years beginning after 2017; line 6 is line 4 less line 5 for
            # every filer.
            applied_income = amt_income

        # Form 6251, Part II top
        # Line 5
        amt_exemption = tax_unit("amt_exemption", period)

        # Line 6
        return max_(0, applied_income - amt_exemption)
