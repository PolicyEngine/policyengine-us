from policyengine_us.model_api import *


class oh_section_179_expense_add_back(Variable):
    value_type = float
    entity = Person
    label = "Ohio Section 179 Expense Add Back"
    definition_period = YEAR
    documentation = ""
    reference = ""
    defined_for = StateCode.OH
    # use federal variables if they are added later
