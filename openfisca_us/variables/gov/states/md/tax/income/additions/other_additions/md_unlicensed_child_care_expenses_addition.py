## md_unlicensed_child_care_expenses_addition.py
from openfisca_us.model_api import *

class md_unlicensed_child_care_expenses_addition(Variable):
    # j. Amount deducted for federal income tax purposes for expenses attributable to operating a family day care home or a child care center in Maryland without having the registration or license required by the Family Law Article.
    value_type = float
    entity = TaxUnit
    label = "MD Unlicensed Child Care Expenses"
    documentation = "Amount deducted for federal income tax purposes for expenses attributable to operating a family day care home or a child care center in Maryland without having the registration or license required by the Family Law Article."
    unit = USD
    definition_period = YEAR