from policyengine_us.model_api import *


class id_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/",  # (j)
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=10",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        itm_ded = tax_unit("id_itemized_deductions", period)
        std_ded = tax_unit("standard_deduction", period)
        itemizes = tax_unit("id_itemizes", period)
        # The election accounts for the associated health premium subtraction.
        # Qualified business income and Schedule 1-A deductions are separate.
        return where(itemizes, itm_ded, std_ded)
