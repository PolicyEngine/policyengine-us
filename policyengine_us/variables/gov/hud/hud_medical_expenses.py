from policyengine_us.model_api import *


class hud_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD medical expenses"
    unit = USD
    documentation = (
        "Medical expenses considered in HUD adjusted income, including "
        "unreimbursed employee-paid health insurance premiums whether paid "
        "through pretax payroll deductions or from non-pretax funds."
    )
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-24/section-5.603",
        "https://www.ecfr.gov/current/title-24/section-5.611",
        "https://www.hud.gov/sites/dfiles/OCHCO/documents/2023-27pihn.pdf#page=37",
    )

    adds = [
        "medical_expense_health_insurance_premiums",
        "pre_tax_health_insurance_premiums",
        "other_medical_expenses",
    ]
