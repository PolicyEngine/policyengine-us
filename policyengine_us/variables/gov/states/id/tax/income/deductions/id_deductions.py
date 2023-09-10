from policyengine_us.model_api import *


class id_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho deductions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/",  # (j)
        "file:///Users/pavelmakarchuk/Desktop/PolicyEngine/Tax%20Forms/Idaho/EFO00089_12-30-2022.pdf#page=4",
    )
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        itm_ded = tax_unit("itemized_deductions_less_salt", period)
        std_ded = tax_unit("standard_deduction", period)
        return max_(itm_ded, std_ded)
