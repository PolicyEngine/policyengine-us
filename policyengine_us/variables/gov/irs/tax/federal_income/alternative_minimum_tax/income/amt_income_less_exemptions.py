from policyengine_us.model_api import *


class amt_income_less_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Alternative Minimum Tax Income less exemptions"
    unit = USD
    documentation = "Alternative Minimum Tax (AMT) income less exemptions"

    def formula(tax_unit, period, parameters):
        # Form 6251, Part I
        # Line 4
        amt_income = tax_unit("amt_income", period)
        # For filers subject to the kiddie tax, the deductions are not added back
        taxable_income = tax_unit("taxable_income", period)
        kiddie_tax_applies = tax_unit("amt_kiddie_tax_applies", period)
        applied_income = where(kiddie_tax_applies, taxable_income, amt_income)

        # Form 6251, Part II top
        # Line 5
        amt_exemption = tax_unit("amt_exemption", period)

        # Line 6
        return max_(0, applied_income - amt_exemption)
