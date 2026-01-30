from policyengine_us.model_api import *


class was_calworks_recipient(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Was a CalWORKs cash aid recipient"
    definition_period = YEAR
    defined_for = StateCode.CA
    default_value = False
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10372.&nodeTreePath=16.4.19&lawCode=WIC"
