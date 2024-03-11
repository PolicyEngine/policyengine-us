from policyengine_us.model_api import *


class id_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho taxable income"
    unit = USD
    documentation = "Idaho taxable income"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_12-30-2022.pdf#page=1"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        agi = tax_unit("id_agi", period)
        deductions = tax_unit("id_deductions", period)
        qbid = tax_unit("qualified_business_income_deduction", period)
        return max_(0, agi - deductions - qbid)
