from policyengine_us.model_api import *


class id_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/(j)"
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        itemizes = tax_unit("tax_unit_itemizes", period)
        itm_ded = tax_unit("itemized_deductions_less_salt", period)
        std_ded = tax_unit("standard_deduction", period)
        return where(itemizes, itm_ded, std_ded)
