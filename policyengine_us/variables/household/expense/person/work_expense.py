from policyengine_us.model_api import *


class work_expense(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Work expenses"
    # For self-employment, report the business expenses already deducted from
    # the corresponding net income, across farm and non-farm businesses.
    # Exclude employee expenses and personal taxes from this business amount.
