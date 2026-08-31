from policyengine_us.model_api import *


class heating_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Heating cost for each person"
    unit = USD
    definition_period = YEAR
    documentation = "Deprecated: heating bills attach to the dwelling, not to people. Set heating_type and the matching per-fuel expense (e.g. gas_expense) instead; this input remains only as a fallback in heating_expense."
