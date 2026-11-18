from policyengine_us.model_api import *


class mi_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MI
    documentation = (
        "Michigan other additions to federal adjusted gross income reported on "
        "Schedule 1, Line 8 (Other additions), entered as a positive amount."
    )
    reference = "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/IIT/TY2024/MI-1040-Instructions.pdf#page=13"
