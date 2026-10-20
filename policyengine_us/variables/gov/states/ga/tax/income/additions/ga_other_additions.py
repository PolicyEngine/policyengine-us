from policyengine_us.model_api import *


class ga_other_additions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia other additions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    documentation = (
        "Georgia other additions to federal adjusted gross income reported on "
        "Form 500, Schedule 1, Line 3 (Other additions), entered as a positive amount."
    )
    reference = "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=21"
