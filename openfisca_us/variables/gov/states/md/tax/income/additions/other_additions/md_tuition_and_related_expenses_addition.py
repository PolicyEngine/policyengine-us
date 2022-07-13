## md_tuition_and_related_expenses_addition.py
from openfisca_us.model_api import *

class md_tuition_and_related_expenses_addition(Variable):
    # o. Amount deducted on your federal income tax return for tuition and related expenses. Do not include adjustments to income for Educator Expenses or Student Loan Interest deduction.
    value_type = float
    entity = TaxUnit
    label = "MD tuition and related expenses"
    documentation = "Amount deducted on your federal income tax return for tuition and related expenses. Do not include adjustments to income for Educator Expenses or Student Loan Interest deduction."
    unit = USD
    definition_period = YEAR