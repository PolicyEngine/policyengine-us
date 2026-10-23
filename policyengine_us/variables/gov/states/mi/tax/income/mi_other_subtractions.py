from policyengine_us.model_api import *


class mi_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    documentation = (
        "Michigan miscellaneous subtractions from federal adjusted gross income "
        "reported on Schedule 1, Line 23 (Miscellaneous subtractions), entered "
        "as a positive amount, excluding subtractions PolicyEngine calculates "
        "separately."
    )
    reference = "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/MI-1040-Instructions.pdf#page=15"
