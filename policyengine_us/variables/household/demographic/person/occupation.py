from policyengine_us.model_api import *


class Occupation(Enum):
    OTHER = "Other"
    MANAGEMENT_BUSINESS_FINANCIAL = "Chief executives, and managers"
    MANAGEMENT_INFRASTRUCTURE = (
        "Compensation, human resources, and infrastructure managers"
    )
    OTHER_MANAGERS = "All other managers"
    ARTIST_AGENTS = (
        "Agents & business managers of artists, performers, and athletes"
    )
    BUSINESS_OPERATIONS = "Business operations specialists"
    ACCOUNTING = "Accountants and auditors"
    FINANCE = "Financial specialists"
    COMPUTER_SCIENCE = "Computer science occupations"
    MATH_SCIENCE = "Mathematical science occupations"
    ARCHITECTURE = "Architects, except naval"
    SURVEYING = "Surveyors, cartographers, & photogrammetrists"
    ENGINEERING_TECH = "Engineering technologists and technicians"
    EARTH_SCIENCE = "Earth scientists"
    ECONOMICS = "Economists"
    SOCIAL_SCIENCE = "Psychologists, and other social scientists"
    HEALTH_SAFETY = "Health and safety specialists"
    COMMUNITY_SERVICE = "Community and social service occupations"
    LEGAL_PRACTICE = "Lawyers, judges, magistrates, and other judicial workers"
    LEGAL_SUPPORT = "Paralegals and all other legal support workers"
    POSTSECONDARY_ED = "Postsecondary teachers"
    OTHER_EDUCATORS = "All other teachers & instructors"
    MUSEUM_EDTECH = (
        "Museum and library technicians and educational instruction workers"
    )
    ARTS_MEDIA = "Arts, design, entertainment, sports, and media occupations"
    SPECIALIZED_HEALTHCARE = "Specialized healthcare practitioners"
    NURSING_THERAPY = (
        "Registered nurses, therapists, and specific pathologists"
    )
    VETERINARY = "Veterinarians"
    HEALTH_TECHNICIANS = (
        "Health technologists & technicians and other healthcare practitioners"
    )
    HEALTHCARE_SUPPORT = "Healthcare support occupations"
    PROTECTIVE_SUPERVISORS = (
        "First-line supervisors of protective service workers"
    )
    FIREFIGHTERS_LAW = "Firefighters & state law enforcement officers"
    PRIVATE_SECURITY = "Private protective service workers"
    COOKS = "Chefs and cooks"
    FOOD_SERVICE = "Food preparation and serving related workers"
    HOUSEKEEPING_SUPERVISORS = (
        "First-line supervisors of housekeeping and janitorial workers"
    )
    JANITORIAL = "Janitors and other grounds maintenance workers"
    PERSONAL_CARE_SUPERVISORS = (
        "Supervisors of personal care and service workers"
    )
    PERSONAL_CARE = "Personal care and service occupations"
    SALES_SUPERVISORS = (
        "First-line supervisors of retail/non-retail sales workers"
    )
    SALES = "Sales and related occupations"
    ADMIN_SUPPORT = "Office & administrative support occupations"
    FARMING_FORESTRY = "Farming, fishing, & forestry occupations"
    CONSTRUCTION_SUPERVISORS = (
        "First-line supervisors of construction trades workers"
    )
    CARPENTRY = "Carpenters"
    FLOOR_INSTALLERS = "Carpet, floor, & tile installers and finishers"
    ELECTRICAL = "Electricians"
    CONSTRUCTION_MISC = "Insulation workers, painters, and other construction and related workers"
    EXTRACTION = "Extraction workers"
    MAINTENANCE = "Installation, maintenance, & repair workers"
    PRODUCTION = "Production occupations"
    TRANSPORT_SUPERVISORS = "Supervisors of transportation & material moving workers, and fligth related workers"
    TRANSPORT_MISC = "All other transportation & material moving occupations"
    MILITARY = "Military specific occupations"
    NEVER_WORKED = "Never worked"


class occupation(Variable):
    value_type = Enum
    possible_values = Occupation
    default_value = Occupation.OTHER
    entity = Person
    label = "occupation"
    definition_period = YEAR

    def formula(person, period, parameters):
        occupation_code = person("detailed_occupation_recode", period)

        # Create an array of consecutive occupation codes from 0 to 53
        conditions = [occupation_code == i for i in range(54)]

        # Map each code to its respective occupation
        return select(
            conditions,
            [
                Occupation.OTHER,
                Occupation.MANAGEMENT_BUSINESS_FINANCIAL,
                Occupation.MANAGEMENT_INFRASTRUCTURE,
                Occupation.OTHER_MANAGERS,
                Occupation.ARTIST_AGENTS,
                Occupation.BUSINESS_OPERATIONS,
                Occupation.ACCOUNTING,
                Occupation.FINANCE,
                Occupation.COMPUTER_SCIENCE,
                Occupation.MATH_SCIENCE,
                Occupation.ARCHITECTURE,
                Occupation.SURVEYING,
                Occupation.ENGINEERING_TECH,
                Occupation.EARTH_SCIENCE,
                Occupation.ECONOMICS,
                Occupation.SOCIAL_SCIENCE,
                Occupation.HEALTH_SAFETY,
                Occupation.COMMUNITY_SERVICE,
                Occupation.LEGAL_PRACTICE,
                Occupation.LEGAL_SUPPORT,
                Occupation.POSTSECONDARY_ED,
                Occupation.OTHER_EDUCATORS,
                Occupation.MUSEUM_EDTECH,
                Occupation.ARTS_MEDIA,
                Occupation.SPECIALIZED_HEALTHCARE,
                Occupation.NURSING_THERAPY,
                Occupation.VETERINARY,
                Occupation.HEALTH_TECHNICIANS,
                Occupation.HEALTHCARE_SUPPORT,
                Occupation.PROTECTIVE_SUPERVISORS,
                Occupation.FIREFIGHTERS_LAW,
                Occupation.PRIVATE_SECURITY,
                Occupation.COOKS,
                Occupation.FOOD_SERVICE,
                Occupation.HOUSEKEEPING_SUPERVISORS,
                Occupation.JANITORIAL,
                Occupation.PERSONAL_CARE_SUPERVISORS,
                Occupation.PERSONAL_CARE,
                Occupation.SALES_SUPERVISORS,
                Occupation.SALES,
                Occupation.ADMIN_SUPPORT,
                Occupation.FARMING_FORESTRY,
                Occupation.CONSTRUCTION_SUPERVISORS,
                Occupation.CARPENTRY,
                Occupation.FLOOR_INSTALLERS,
                Occupation.ELECTRICAL,
                Occupation.CONSTRUCTION_MISC,
                Occupation.EXTRACTION,
                Occupation.MAINTENANCE,
                Occupation.PRODUCTION,
                Occupation.TRANSPORT_SUPERVISORS,
                Occupation.TRANSPORT_MISC,
                Occupation.MILITARY,
                Occupation.NEVER_WORKED,
            ],
            default=Occupation.OTHER,
        )
