from policyengine_us.model_api import *


class Occupation(Enum):
    OTHER = "other"
    MANAGEMENT_BUSINESS_FINANCIAL = "management, business and financial"
    PROFESSIONAL_RELATED = "professional and related"
    SERVICE = "service"
    SALES = "sales and related"
    OFFICE_ADMINISTRATIVE = "office and administrative support"
    FARMING_FISHING_FORESTRY = "farming, fishing and forestry"
    CONSTRUCTION_EXTRACTION = "construction and extraction"
    INSTALLATION_MAINTENANCE_REPAIR = "installation, maintenance and repair"
    PRODUCTION = "production"
    TRANSPORTATION_MATERIAL_MOVING = "transportation and material moving"
    MILITARY = "military"


class occupation(Variable):
    value_type = Enum
    possible_values = Occupation
    default_value = Occupation.OTHER
    entity = Person
    label = "occupation"
    definition_period = YEAR

    def formula(person, period, parameters):
        occupation_code = person("major_occupation_recode", period)
        return select(
            [
                occupation_code == 0,
                occupation_code == 1,
                occupation_code == 2,
                occupation_code == 3,
                occupation_code == 4,
                occupation_code == 5,
                occupation_code == 6,
                occupation_code == 7,
                occupation_code == 8,
                occupation_code == 9,
                occupation_code == 10,
                occupation_code == 11,
            ],
            [
                Occupation.OTHER,
                Occupation.MANAGEMENT_BUSINESS_FINANCIAL,
                Occupation.PROFESSIONAL_RELATED,
                Occupation.SERVICE,
                Occupation.SALES,
                Occupation.OFFICE_ADMINISTRATIVE,
                Occupation.FARMING_FISHING_FORESTRY,
                Occupation.CONSTRUCTION_EXTRACTION,
                Occupation.INSTALLATION_MAINTENANCE_REPAIR,
                Occupation.PRODUCTION,
                Occupation.TRANSPORTATION_MATERIAL_MOVING,
                Occupation.MILITARY,
            ],
            default=Occupation.OTHER,
        )
