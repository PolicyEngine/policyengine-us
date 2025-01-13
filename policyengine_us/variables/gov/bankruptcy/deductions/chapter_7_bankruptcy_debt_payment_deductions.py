from policyengine_us.model_api import *


class chapter_7_bankruptcy_debt_payment_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy debt payment deductions"
    definition_period = MONTH
    reference = "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=7"

    adds = ["housing_cost", "vehicle_mortgage_expense"]
