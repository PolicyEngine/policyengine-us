from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    state_non_refundable_credit_limit,
)


class va_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia rebate"
    unit = USD
    documentation = (
        "The one-time Virginia income tax rebate, limited to the tax liability "
        "after every deduction, subtraction and credit under Chapter 3 of "
        "Title 58.1, including the refundable Virginia EITC."
    )
    definition_period = YEAR
    reference = (
        # 2021 return: 2022 Special Session I, HB30 (Chapter 2), Item 3-5.22.
        "https://budget.lis.virginia.gov/item/2022/2/HB30/Chapter/3/3-5.22/",
        # 2022 return: 2023 Special Session I, HB6001 (Chapter 1), Item 3-5.28 B.
        "https://budget.lis.virginia.gov/item/2023/2/HB6001/Chapter/3/3-5.28/",
        # 2024 return: 2025 Session, HB1600 (Chapter 725), Item 258 GG.3.
        "https://budget.lis.virginia.gov/item/2025/1/HB1600/Chapter/1/258/",
        # The refundable EITC is a Chapter 3 credit: Va. Code 58.1-339.8 B 3.
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        "https://www.tax.virginia.gov/rebate",
    )
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income
        filing_status = tax_unit("filing_status", period)
        amount = p.rebate.amount[filing_status]
        # Each act allows the refund only "up to the amount of such
        # individual's tax liability after the application of any
        # deductions, subtractions, or credits to which the individual is
        # entitled pursuant to Chapter 3". That is the Form 760 Line 18 net
        # tax (after the Spouse Tax Adjustment) less the Line 23 credit,
        # which is either a non-refundable credit or the refundable EITC.
        # Reading the refundable EITC here has no cycle: va_claims_refundable_eitc
        # compares va_income_tax in branches that set it as an input.
        tax_after_non_refundable_credits = state_non_refundable_credit_limit(
            tax_unit,
            period,
            p.credits.non_refundable,
            "va_income_tax_before_non_refundable_credits",
            "va_rebate",
        )
        spouse_tax_adjustment = tax_unit("va_spouse_tax_adjustment", period)
        refundable_credits = tax_unit("va_refundable_credits", period)
        tax_liability = max_(
            tax_after_non_refundable_credits
            - spouse_tax_adjustment
            - refundable_credits,
            0,
        )
        return min_(amount, tax_liability)
