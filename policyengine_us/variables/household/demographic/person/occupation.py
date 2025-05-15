from policyengine_us.model_api import *


class Occupation(Enum):
    OTHER = 0
    MANAGEMENT_BUSINESS_FINANCIAL = 1
    PROFESSIONAL_RELATED = 2
    SERVICE = 3
    SALES = 4
    OFFICE_ADMINISTRATIVE = 5
    FARMING_FISHING_FORESTRY = 6
    CONSTRUCTION_EXTRACTION = 7
    INSTALLATION_MAINTENANCE_REPAIR = 8
    PRODUCTION = 9
    TRANSPORTATION_MATERIAL_MOVING = 10
    MILITARY_SPECIFIC = 11


class occupation(Variable):
    value_type = Enum
    possible_values = Occupation
    default_value = Occupation.OTHER
    entity = Person
    label = "Occupation"
    definition_period = YEAR
