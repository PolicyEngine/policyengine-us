from policyengine_us.model_api import *


class ca_care_categorically_eligible(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Eligible for California CARE program by virtue of participation in a qualiifying program"
    documentation = "Eligible for California Alternate Rates for Energy"
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PUC&sectionNum=739.1"
    defined_for = StateCode.CA
    adds = "gov.states.ca.cpuc.care.eligibility.categorical"
