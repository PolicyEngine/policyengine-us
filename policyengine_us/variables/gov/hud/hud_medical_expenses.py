from policyengine_us.model_api import *


class hud_medical_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "HUD medical expenses"
    unit = USD
    documentation = "Medical expenses considered in HUD adjusted income."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/24/5.611"

    adds = [
        "medical_expense_health_insurance_premiums",
        "other_medical_expenses",
    ]
