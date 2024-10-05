from policyengine_us.model_api import *


class ca_care_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1"
    defined_for = StateCode.CA
    adds = ["ca_care_categorically_eligible", "ca_care_income_eligible"]
