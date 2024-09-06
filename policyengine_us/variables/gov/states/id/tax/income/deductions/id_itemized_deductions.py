from policyengine_us.model_api import *


class id_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-01-2023.pdf#page=8",
        "https://tax.idaho.gov/wp-content/uploads/forms/EFO00089/EFO00089_09-23-2021.pdf",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        # Idaho reduces the federal itemized deductions
        # by the amount of the SALT deduction
        id_salt_ded = tax_unit("id_salt_deduction", period)
        itemized_ded = tax_unit("itemized_taxable_income_deductions", period)
        return max_(itemized_ded - id_salt_ded, 0)
