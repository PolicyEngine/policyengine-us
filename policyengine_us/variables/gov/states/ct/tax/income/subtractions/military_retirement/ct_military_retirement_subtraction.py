from policyengine_us.model_api import *


class ct_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut military retirement subtraction"
    unit = USD
    definition_period = YEAR
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2022/Income/2022-CT-1040-Instructions_1222.pdf#page=9"
    defined_for = StateCode.CT

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        # Only taxable military retirement income is considered
        military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        exclusion_amount = min_(military_retirement_pay, agi)
        return max_(0, military_retirement_pay - exclusion_amount)
