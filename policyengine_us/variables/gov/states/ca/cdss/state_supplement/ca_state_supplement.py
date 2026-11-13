from policyengine_us.model_api import *


class ca_state_supplement(Variable):
    value_type = float
    entity = SPMUnit
    label = "California state supplement"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=WIC&sectionNum=12200"
    adds = ["ca_state_supplement_person"]
