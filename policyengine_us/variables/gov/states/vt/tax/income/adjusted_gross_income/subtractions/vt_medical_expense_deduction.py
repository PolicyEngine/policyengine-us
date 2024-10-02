from policyengine_us.model_api import *


class vt_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont medical expense deduction"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(C)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=2",  # Instruction for 2022 SCHEDULE IN-112 - MEDICAL DEDUCTION WORKSHEET
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont medical expenses deducted from taxable income."

    def formula(tax_unit, period, parameters):
        # Get federal medical expense deduction (Worksheet line 1a).
        # This points to federal Form 1040, Schedule A, Line 4, which is the deduction itself
        # (not the expenses).
        # The law says "an amount equal to the itemized deduction for medical expenses
        # taken at the federal level by the taxpayer" but does not state whether the filer
        # must have itemized on the federal return to claim it.
        # We assume they do not have to, based on the form.
        federal_medical_expense_deduction = tax_unit(
            "medical_expense_deduction", period
        )
        # Get Vermont standard deduction plus personal exemptions (Worksheet line 2).
        vt_standard_deduction = tax_unit("vt_standard_deduction", period)
        vt_personal_exemptions = tax_unit("vt_personal_exemptions", period)
        # Subtract standard deduction plus personal exemptions from vt allowed medical expense deduction and return (Worksheet line 3).
        return max_(
            0,
            federal_medical_expense_deduction
            - vt_standard_deduction
            - vt_personal_exemptions,
        )
