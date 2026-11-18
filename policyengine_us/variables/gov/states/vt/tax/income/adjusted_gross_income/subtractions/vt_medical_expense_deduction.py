from policyengine_us.model_api import *


class vt_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont medical expense deduction"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(C)(iv)
        "https://tax.vermont.gov/medical-deduction",
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont medical expenses deducted from taxable income."

    def formula_2019(tax_unit, period, parameters):
        # IN-112 starts from medical expenses claimed on federal Schedule A, line 4.
        itemizes = tax_unit("tax_unit_itemizes", period)
        medical = tax_unit("medical_expense_deduction", period)
        standard = tax_unit("vt_standard_deduction", period)
        exemptions = tax_unit("vt_personal_exemptions", period)
        return where(itemizes, max_(0, medical - standard - exemptions), 0)
