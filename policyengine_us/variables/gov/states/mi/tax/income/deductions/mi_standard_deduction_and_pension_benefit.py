from policyengine_us.model_api import *


class mi_standard_deduction_and_pension_benefit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan standard deduction, consist of standard deduction for age 67-76, retirement and pension benefits for age 62-66 and above 77, and interest, dividends, and capital gains deduction for age above 77."
    reference = (
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits/michigan-standard-deduction",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
        "https://www.michigan.gov/taxes/iit/retirement-and-pension-benefits",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        return (
            tax_unit("mi_standard_deduction", period)
            + tax_unit("mi_retirement_benefits_deduction_tier_one", period)
            + tax_unit("mi_retirement_benefits_deduction_tier_three", period)
            + tax_unit("mi_interest_dividends_capital_gains_deduction", period)
        )
