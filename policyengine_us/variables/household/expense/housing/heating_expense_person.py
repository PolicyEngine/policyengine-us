from policyengine_us.model_api import *


class heating_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Heating cost for each person"
    unit = USD
    definition_period = YEAR
    documentation = "Deprecated: heating bills attach to the dwelling, not to people. Set heating_type and the matching per-fuel expense (e.g. gas_expense) instead; this input remains only as a fallback inside the DC, IL and MA LIHEAP adapters for households whose heating_type is UNSPECIFIED, and as the source of the tax-unit heating_expenses used by the Michigan home heating credit."
