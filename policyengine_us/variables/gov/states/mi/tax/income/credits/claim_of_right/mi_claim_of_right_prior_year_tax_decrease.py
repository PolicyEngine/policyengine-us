from policyengine_us.model_api import *


class mi_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = "Michigan prior-year tax on repaid claim of right income"
    unit = USD
    documentation = (
        "Michigan income tax paid in the earlier year or years that is "
        "attributable to the income repaid this year "
        "(claim_of_right_repayment). Michigan figures it as the amount "
        "repaid times the Michigan income tax rate in effect for the year "
        "the income was taxed. The tax unit uses the sum for its head and "
        "spouse."
    )
    definition_period = YEAR
    reference = (
        "https://www.legislature.mi.gov/Laws/MCL?objectName=mcl-206-265",
        # Revenue Administrative Bulletin 1994-9, Calculation of the Credit
        "https://www.michigan.gov/treasury/reference/rab/content/1994/revenue-administrative-bulletin-1994-9",
        # 2025 MI-1040 instruction book, Repayments of Income Reported in a
        # Prior Year
        "https://www.michigan.gov/-/media/Project/Websites/taxes/Forms/IIT/TY2025/MI-1040-Book.pdf#page=8",
    )
    defined_for = StateCode.MI
