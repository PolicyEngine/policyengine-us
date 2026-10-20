from policyengine_us.model_api import *


class md_military_retirement_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland military retirement income subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-207",
        # Code letter u, military retirement income.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=17",
        # Filing status 6: a person who can be claimed as a dependent files
        # their own return as a dependent taxpayer.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )

    adds = ["md_military_retirement_subtraction_amount"]
