from policyengine_us.model_api import *


class chapter_7_bankruptcy_adjusted_monthly_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Chapter 7 Bankruptcy adjust monthly income"
    definition_period = MONTH
    reference = (
        "https://www.uscourts.gov/sites/default/files/form_b122a-1.pdf#page=1",
        "https://www.cacb.uscourts.gov/sites/cacb/files/documents/forms/122A2.pdf#page=1",
    )
    documentation = "Line 4 in form 122A-2"

    adds = [
        "irs_employment_income",
        "alimony_income",
        "child_support_received",
        "partnership_s_corp_income",
        "farm_income",
        "farm_rent_income",
        "rental_income",
        "dividend_income",
        "interest_income",
        "unemployment_compensation",
        "pension_income",
        "retirement_distributions",
    ]
