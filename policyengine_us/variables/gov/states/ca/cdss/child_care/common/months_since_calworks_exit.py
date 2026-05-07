from policyengine_us.model_api import *


class months_since_calworks_exit(Variable):
    value_type = int
    entity = SPMUnit
    label = "Months since CalWORKs cash aid ended"
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=10372.&nodeTreePath=16.4.19&lawCode=WIC"
