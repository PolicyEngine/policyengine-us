from policyengine_us.model_api import *


class dwks06(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "IRS Form 1040 Schedule D worksheet (part 1 of 6)"
    unit = USD

    def formula(tax_unit, period, parameters):
        dwks02 = add(tax_unit, period, ["qualified_dividend_income"])
        dwks03 = tax_unit("investment_income_form_4952", period)
        # dwks04 always assumed to be zero
        dwks05 = max_(0, dwks03)
        return max_(0, dwks02 - dwks05)
