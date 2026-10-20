from policyengine_us.model_api import *


class md_other_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland other subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    documentation = (
        "Maryland other subtractions from federal adjusted gross income reported on "
        "Form 502SU / Form 502, Line 13 (Subtractions from income), entered as a positive amount. "
        "Do not include U.S. government interest, dependent care, pension, Social Security, "
        "two-income, hundred-year, military retirement, 529, or state tax refund subtractions, "
        "which PolicyEngine computes separately."
    )
    reference = "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=16"
