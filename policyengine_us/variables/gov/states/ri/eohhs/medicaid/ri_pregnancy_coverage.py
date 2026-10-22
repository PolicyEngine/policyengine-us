from policyengine_us.model_api import *


class RIPregnancyCoverage(Enum):
    MEDICAID = "Medicaid"
    CHIP = "Separate CHIP"
    RITE_START = "RIte Start"
    FCEP = "CHIP unborn-child coverage"
    NONE = "No established qualifying pregnancy eligibility"


class ri_pregnancy_coverage(Variable):
    # Eligibility during the last completed pregnancy, including retroactive
    # eligibility. Current income and enrollment cannot establish this history.
    value_type = Enum
    possible_values = RIPregnancyCoverage
    default_value = RIPregnancyCoverage.NONE
    entity = Person
    label = "Qualifying Rhode Island coverage during the last completed pregnancy"
    definition_period = YEAR
    reference = (
        "https://webserver.rilegislature.gov/Statutes/TITLE42/42-12.3/42-12.3-3.htm",
        "https://www.medicaid.gov/CHIP/Downloads/RI-22-0025.pdf#page=4",
    )
