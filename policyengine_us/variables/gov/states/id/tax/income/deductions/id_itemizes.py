from policyengine_us.model_api import *


class id_itemizes(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tax unit itemizes deductions for Idaho"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022/",  # (j)
        "https://legislature.idaho.gov/statutesrules/idstat/Title63/T63CH30/SECT63-3022P/",
        # PDF pages 10, 48-49 (Form 40 election and Form 39R premiums).
        "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_03-02-2026.pdf#page=10",
    )
    documentation = (
        "Choose the larger combined Idaho deduction and health premium "
        "subtraction. Itemization removes health premiums already included "
        "in the medical deduction; the standard election preserves them. "
        "Ties retain the standard deduction, unless itemization is required."
    )

    def formula(tax_unit, period, parameters):
        premiums = tax_unit("id_qualified_health_insurance_premiums", period)
        medical = tax_unit("id_health_insurance_premiums_medical_deduction", period)
        # Form 39R allocates itemized medical deductions to health premiums first.
        overlap = min_(premiums, medical)
        itemized = tax_unit("id_itemized_deductions", period)
        standard = tax_unit("standard_deduction", period)
        mandatory = tax_unit("separate_filer_itemizes", period)
        return mandatory | (itemized > standard + overlap)
