from policyengine_us.model_api import *


class vt_non_allow_medical_expense_deductions(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Vermont non-allowable medical and dental expense deductions"
    reference = (
        "https://legislature.vermont.gov/statutes/section/32/151/05811"  # Titl. 32 V.S.A. § 5811(21)(C)(iv)
        "https://tax.vermont.gov/sites/tax/files/documents/IN-112%20Instr-2022.pdf#page=2"  # Instruction for 2022 SCHEDULE IN-112 - MEDICAL DEDUCTION WORKSHEET
    )
    unit = USD
    defined_for = StateCode.VT
    documentation = "Vermont non-allowable medical and dental expense deductions included in federal medical and dental expense deductions. The value equals to recurring monthly payments or entrance fees paid to a retirement community."
