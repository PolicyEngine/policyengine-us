from policyengine_us.model_api import *


class mi_interest_dividends_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan standard deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan interest, dividends, and capital gains deduction for age above 77."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf?rev=86a928564e3f42449c531309673f5da7&hash=7147C48E7C9B1B8171B72DC34A66642A",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.interest_dividends_capital_gains
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)

        age_older = tax_unit("greater_age_head_spouse", period)
        # Interest, Dividends, and Capital Gains Deduction
        idcg_aged_eligibility = age_older >= p.senior_age
        idcg_amount_per_aged = p.senior_amount[filing_status]
        income = tax_unit("mi_interest_dividends_capital_gains_income", period)

        return min_(idcg_aged_eligibility * idcg_amount_per_aged, income)
