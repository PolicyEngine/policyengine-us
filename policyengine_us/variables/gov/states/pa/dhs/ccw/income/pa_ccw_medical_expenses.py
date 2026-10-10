from policyengine_us.model_api import *


class pa_ccw_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania CCW medical expenses"
    unit = USD
    documentation = (
        "Medical expenses deducted from Pennsylvania CCW income, including "
        "employee-paid health premiums paid through pretax payroll deductions "
        "and after-tax payments."
    )
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=61"

    # Appendix A Part I(A) counts wages before health insurance deductions;
    # Part II(C) permits unreimbursed health care premiums without a tax test.
    adds = [
        "medical_expense_health_insurance_premiums",
        "pre_tax_health_insurance_premiums",
        "other_medical_expenses",
    ]
