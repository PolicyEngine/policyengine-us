from policyengine_us.model_api import *


class hi_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI
    documentation = (
        "Hawaii other additions to federal adjusted gross income reported on "
        "Form N-11, Line 9 (Other additions), entered as a positive amount."
    )
    reference = "https://files.hawaii.gov/tax/forms/2025/n11ins.pdf#page=11"
