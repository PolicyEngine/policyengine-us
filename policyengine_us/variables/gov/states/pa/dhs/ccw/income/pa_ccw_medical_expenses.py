from policyengine_us.model_api import *


class pa_ccw_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Pennsylvania CCW medical expenses"
    unit = USD
    documentation = "Medical expenses deducted from Pennsylvania CCW income."
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=18"

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]
