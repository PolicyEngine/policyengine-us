from policyengine_us.model_api import *


class vt_medical_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont medical expense deduction"
    reference = [
        "https://legislature.vermont.gov/statutes/section/32/151/05811",  # Titl. 32 V.S.A. § 5811(21)(C)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf",  # Instruction for 2022 SCHEDULE IN-112 - MEDICAL DEDUCTION WORKSHEET
    ]
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont medical expenses deducted from taxable income."

    def formula(tax_unit, period, parameters):
        # Get federal medical expense deduction (Worksheet line 1a).
        federal_medical_expense_deduction = tax_unit(
            "medical_expense_deduction", period
        )
        # Get Non-allowable federal medical expense deduction (Worksheet line 1b).
        vt_non_allow_medical_expense_deductions = tax_unit(
            "vt_non_allow_medical_expense_deductions", period
        )
        # Subtract non-allowable deduction from federal medical expense deduction (Worksheet line 1c).
        vt_allow_medical_expense_deduction = max_(
            0,
            federal_medical_expense_deduction
            - vt_non_allow_medical_expense_deductions,
        )
        # Get Vermont standard deduction plus personal exemptions (Worksheet line 2).
        vt_standard_deduction = tax_unit("vt_standard_deduction", period)
        vt_personal_exemptions = tax_unit("vt_personal_exemptions", period)
        # Subtract standard deduction plus personal exemptions from vt allowed medical expense deduction and return (Worksheet line 3).
        return max_(
            0,
            vt_standard_deduction
            + vt_personal_exemptions
            - vt_allow_medical_expense_deduction,
        )
