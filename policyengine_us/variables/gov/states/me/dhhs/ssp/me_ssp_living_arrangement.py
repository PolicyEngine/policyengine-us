from policyengine_us.model_api import *


class MESSPCategory(Enum):
    LIVING_ALONE_OR_WITH_OTHERS = "Living alone or with others"
    HOUSEHOLD_OF_ANOTHER = "Household of another"
    ADULT_FOSTER_HOME = "Adult Foster Home"
    FLAT_RATE_BOARDING_HOME = "Flat Rate Boarding Home"
    ADULT_FAMILY_CARE_HOME = "Adult Family Care Home"
    COST_REIMBURSED_BOARDING_HOME = "Cost Reimbursed Boarding Home"
    MEDICAID_FACILITY = "Medicaid facility (Title XIX)"
    RESIDENTIAL_CARE_FACILITY = "Residential Care Facility"
    NONE = "None"


class me_ssp_living_arrangement(Variable):
    value_type = Enum
    entity = Person
    label = "Maine SSP living arrangement"
    definition_period = MONTH
    defined_for = StateCode.ME
    possible_values = MESSPCategory
    default_value = MESSPCategory.LIVING_ALONE_OR_WITH_OTHERS
    reference = (
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/inline-files/144c332-2025-101%20%28AMD%29_0.docx",
        "https://www.maine.gov/sos/sites/maine.gov.sos/files/content/assets/144c332-appendices-charts.docx",
    )
