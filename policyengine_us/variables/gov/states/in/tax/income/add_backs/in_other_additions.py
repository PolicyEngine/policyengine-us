from policyengine_us.model_api import *


class in_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    documentation = (
        "Indiana other add-backs reported on Form IT-40, Schedule 1, Line 6 "
        "(Other Add-Backs), entered as a positive amount, excluding items PolicyEngine calculates separately."
    )
    # PDF pages 13-16
    reference = "https://forms.in.gov/Download.aspx?id=16915#page=13"
