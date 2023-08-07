from policyengine_us.model_api import *


class mi_interest_dividends_capital_gains_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan interest, dividends, and capital gains deduction"
    unit = USD
    definition_period = YEAR
    documentation = "Michigan interest, dividends, and capital gains deduction of qualifying age."
    reference = (
        "http://legislature.mi.gov/doc.aspx?mcl-206-30",  # (p)
        "https://www.michigan.gov/taxes/-/media/Project/Websites/taxes/Forms/2022/2022-IIT-Forms/BOOK_MI-1040.pdf#page=16",
    )
    defined_for = StateCode.MI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mi.tax.income.deductions.interest_dividends_capital_gains
        # Core deduction based on filing status.
        filing_status = tax_unit("filing_status", period)
        age_older = tax_unit("greater_age_head_spouse", period)
        # Interest, Dividends, and Capital Gains Deduction for senior citizens
        idcg_aged_eligibility = age_older >= p.senior_age
        idcg_amount = p.senior_amount[filing_status]
        income = add(tax_unit, period, p.income_types)
        # The maximum amount of the deduction will be reduced by the amount of the
        # deduction claimed for retirement or pension benefits under
        # subdivision (e) or a deduction claimed under subdivision (f)(i), (ii), (iv), or (v)
        military_retirement_deduction = tax_unit(
            "mi_military_retirement_pay_deduction", period
        )

        return min_(idcg_aged_eligibility * idcg_amount, income)
