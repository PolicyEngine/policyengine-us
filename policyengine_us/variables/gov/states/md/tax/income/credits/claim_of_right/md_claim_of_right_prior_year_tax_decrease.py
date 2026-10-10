from policyengine_us.model_api import *


class md_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = (
        "Maryland prior-year tax decrease from excluding repaid claim of right income"
    )
    unit = USD
    documentation = (
        "Total Maryland state and local income tax reported for the earlier "
        "year or years in which the income repaid this year "
        "(claim_of_right_repayment) was received, less the tax that would "
        "have been owed for that year had the repaid income never been "
        "received. The tax unit uses the sum for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        # Administrative Release No. 40, section IV.B, steps (1) to (3)
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/legal-publications/administrative-releases/income-and-estate-tax/ar_it40.pdf#page=3",
    )
    defined_for = StateCode.MD
