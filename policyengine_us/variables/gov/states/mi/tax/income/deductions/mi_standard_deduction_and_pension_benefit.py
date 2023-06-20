from policyengine_us.model_api import *


class mi_standard_deduction_and_pension_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, consist of standard deduction for age 67-76, retirement and pension benefits for age 62-66 and above 77, and interest, dividends, and capital gains deduction for age above 77."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    adds = [
        "mi_standard_deduction",
        "mi_retirement_benefits_deduction_tier_one",
        "mi_retirement_benefits_deduction_tier_three",
        "mi_interest_dividends_capital_gains_deduction",
    ]
