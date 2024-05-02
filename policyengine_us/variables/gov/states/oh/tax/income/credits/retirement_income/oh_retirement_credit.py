from policyengine_us.model_api import *


class oh_retirement_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio Retirement Income Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-5747.055"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        retirement_credit = tax_unit(
            "oh_pension_based_retirement_income_credit", period
        )
        lump_sum_credit = tax_unit("oh_lump_sum_retirement_credit", period)
        return max_(retirement_credit, lump_sum_credit)
