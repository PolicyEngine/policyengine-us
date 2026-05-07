from policyengine_us.model_api import *


class oh_educator_expense_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Ohio educator expense deduction"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.OH
