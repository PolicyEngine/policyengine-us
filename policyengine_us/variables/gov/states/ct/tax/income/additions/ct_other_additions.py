from policyengine_us.model_api import *


class ct_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    documentation = (
        "Connecticut other additions to federal adjusted gross income reported on "
        "Form CT-1040, Schedule 1, Line 37 (Other additions), entered as a positive amount."
    )
    reference = "https://portal.ct.gov/-/media/drs/forms/2025/income/2025-ct-1040-instructions_1225.pdf#page=9"
