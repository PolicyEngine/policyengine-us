from policyengine_us.model_api import *


class in_section_179_expense_add_back(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana Section 179 Expense Add Back"
    definition_period = YEAR
    documentation = "Federal IRC Section 179 expenses less IRC Section 179 expenses if they had been calculated with a $25,000 ceiling."
    reference = "http://iga.in.gov/legislative/laws/2021/ic/titles/006#6-3-1-3.5"  # (a)(17)(A)
    # use federal variables if they are added later
