from policyengine_us.model_api import *


class heating_expense_person(Variable):
    value_type = float
    entity = Person
    label = "Heating cost for each person"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Deprecated: set heating_type and the matching per-fuel expense "
        "(e.g. gas_expense) for shared heating bills. For Michigan "
        "claimant-specific costs, including shares of a bill and the "
        "November-October billing period, set heating_expenses directly. "
        "This input remains a fallback inside the DC, IL and MA LIHEAP "
        "adapters and the tax-unit heating_expenses used by the Michigan "
        "home heating credit, for households whose heating_type is UNSPECIFIED."
    )
