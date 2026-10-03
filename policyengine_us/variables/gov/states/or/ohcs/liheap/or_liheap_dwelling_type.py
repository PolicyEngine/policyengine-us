from policyengine_us.model_api import *


class ORLIHEAPDwellingType(Enum):
    STANDARD = "Standard household"
    ROOMER_BOARDER_OWNER = (
        "Roomer, boarder or owner applying separately from other residents"
    )


class or_liheap_dwelling_type(Variable):
    value_type = Enum
    possible_values = ORLIHEAPDwellingType
    default_value = ORLIHEAPDwellingType.STANDARD
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP dwelling arrangement"
    # PDF pages 30, 61, 62.
    reference = "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=30"
    documentation = "The half-payment arrangement applies when a roomer, boarder or owner applies as a separate economic household and the other residents do not apply together. It is not a reduction for all renters."
