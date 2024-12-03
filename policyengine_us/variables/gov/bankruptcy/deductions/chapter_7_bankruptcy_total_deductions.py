from policyengine_us.model_api import *


class chapter_7_bankruptcy_total_deductions(Variable):
    value_type = float
    entity = SPMUnit
    label = "Total deductions from Income"
    unit = USD
    definition_period = YEAR

    adds = [
        "chapter_7_bankruptcy_national_standards_deductions",
        "chapter_7_bankruptcy_local_standards_deductions",
        "chapter_7_bankruptcy_other_necessary_expenses_deductions",
        "chapter_7_bankruptcy_additional_expense_deductions",
        "chapter_7_bankruptcy_debt_payment_deductions",
    ]
