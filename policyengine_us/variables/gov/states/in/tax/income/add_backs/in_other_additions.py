from policyengine_us.model_api import *


class in_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    documentation = (
        "Indiana other add-backs reported on Form IT-40, Schedule 1, Line 2 "
        "(Other Add-Backs), entered as a positive amount, excluding items PolicyEngine calculates separately."
    )
    reference = "https://www.in.gov/dor/files/reference/2024-it-40-booklet.pdf#page=15"
