from policyengine_us.model_api import *


class id_health_insurance_premiums_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho health insurance premiums subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # PDF pages 48-49 (Form 39R, line 18 and its worksheet).
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=48",
    )

    def formula(tax_unit, period, parameters):
        premiums = tax_unit("id_qualified_health_insurance_premiums", period)
        medical = tax_unit("medical_expense_deduction", period)
        overlap = min_(premiums, medical)
        itemizes = tax_unit("id_itemizes", period)
        return premiums - where(itemizes, overlap, 0)
