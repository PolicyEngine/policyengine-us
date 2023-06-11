from policyengine_us.model_api import *


class mi_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan taxable income"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        std_ded = tax_unit("mi_standard_deduction", period)
        itm_ded = tax_unit(
            "itemized_taxable_income_deductions", period
        )  # equal to federal itmded
        deductions = where(itm_ded > std_ded, itm_ded, std_ded)
        exemptions = tax_unit("mi_exemptions", period)
        return max_(0, agi - deductions - exemptions)
