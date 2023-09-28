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
        adjusted_gross_income = add(
            tax_unit, period, ["adjusted_gross_income"]
        )
        military_retirement_pay = add(
            tax_unit, period, ["military_retirement_pay"]
        )
        exclusion_amount = min_(military_retirement_pay, adjusted_gross_income)
        return military_retirement_pay - exclusion_amount
