from policyengine_us.model_api import *


class az_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = "Arizona prior-year tax decrease from excluding repaid claim of right income"
    unit = USD
    documentation = (
        "Decrease in Arizona income tax for the earlier year or years that "
        "would result solely from excluding from gross income the amount "
        "repaid this year (claim_of_right_repayment): the tax on the Arizona "
        "return filed for the earlier year less that tax refigured without "
        "the repaid income (Arizona Claim of Right form, lines 6 to 8). The "
        "tax unit uses the sum for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        "https://www.azleg.gov/ars/43/01029.htm",
        # 2025 Arizona Claim of Right - Individual instructions, Part 2
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_CLAIMOFRIGHT-INDIVIDUALi.pdf#page=2",
        # ITP 16-1, Tax Computation
        "https://azdor.gov/sites/default/files/2023-03/PROCEDURES_INDIV_2016_ITP16-1.pdf#page=3",
    )
    defined_for = StateCode.AZ
