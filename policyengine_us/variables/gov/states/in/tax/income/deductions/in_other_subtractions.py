from policyengine_us.model_api import *


class in_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Indiana other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IN
    documentation = (
        "Indiana other deductions reported on Form IT-40, Schedule 2, Line 11 "
        "(Other Deductions), entered as a positive amount, excluding items PolicyEngine calculates separately."
    )
    reference = "https://www.in.gov/dor/files/reference/2024-it-40-booklet.pdf#page=19"
