from policyengine_us.model_api import *


class IDAAbdLivingArrangement(Enum):
    SINGLE = "Single participant"
    COUPLE = "Couple"
    ESSENTIAL_PERSON = "Participant with essential person"
    SIGRIF = "Semi-independent group residential facility"
    ROOM_AND_BOARD = "Room and board"
    RALF_CFH = "Residential assisted living facility or certified family home"
    NONE = "Not applicable"


class id_aabd_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Idaho AABD living arrangement"
    definition_period = MONTH
    defined_for = StateCode.ID
    possible_values = IDAAbdLivingArrangement
    default_value = IDAAbdLivingArrangement.NONE
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160305.pdf#page=39",
        "https://www.law.cornell.edu/regulations/idaho/IDAPA-16.03.05.514",
    )
