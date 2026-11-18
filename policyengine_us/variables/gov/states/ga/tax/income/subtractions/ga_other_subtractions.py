from policyengine_us.model_api import *


class ga_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Georgia other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.GA
    documentation = (
        "Georgia other subtractions from federal adjusted gross income reported on "
        "Form 500, Schedule 1, Line 12 (Other subtractions), entered as a positive amount. "
        "Do not include U.S. government interest, retirement/military exclusions, "
        "Social Security, 529 plan contributions, or overtime/tip exclusions, "
        "which PolicyEngine computes separately."
    )
    reference = "https://dor.georgia.gov/document/document/2025-it-511-individual-income-tax-booklet/download#page=21"
