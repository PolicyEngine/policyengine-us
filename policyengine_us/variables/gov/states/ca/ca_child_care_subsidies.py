from policyengine_us.model_api import *


class ca_child_care_subsidies(Variable):
    value_type = float
    entity = SPMUnit
    label = "California child care subsidies"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.CA
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?lawCode=WIC&division=9.&title=&part=1.8.&chapter=2.&article="
    adds = [
        "ca_calworks_child_care",
        "ca_calworks_stage_2",
        "ca_calworks_stage_3",
        "ca_capp",
    ]
