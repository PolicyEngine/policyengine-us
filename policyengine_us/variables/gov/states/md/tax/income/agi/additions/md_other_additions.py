from policyengine_us.model_api import *


class md_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    documentation = (
        "Maryland other additions to federal adjusted gross income reported on "
        "Form 502, Line 5 (Other additions), entered as a positive amount."
    )
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=9"
