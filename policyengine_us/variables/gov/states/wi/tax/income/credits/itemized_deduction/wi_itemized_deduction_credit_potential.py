from policyengine_us.model_api import *


class wi_itemized_deduction_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "Wisconsin itemized deduction credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1f.pdf#page=4",
        "https://www.revenue.wi.gov/TaxForms2021/2021-Form1NPR-Inst.pdf#page=34",
        "https://www.revenue.wi.gov/TaxForms2022/2022-Form1f.pdf#page=4",
        "https://docs.legis.wisconsin.gov/misc/lfb/informational_papers/january_2023/0002_individual_income_tax_informational_paper_2.pdf#page=19",
        # Wis. Stat. 71.07(5)(a)
        "https://docs.legis.wisconsin.gov/statutes/statutes/71.pdf#page=39",
        "https://www.revenue.wi.gov/TaxForms2025/2025-Form1.pdf#page=4",
    )
    defined_for = StateCode.WI

    def formula(tax_unit, period, parameters):
        # Wis. Stat. 71.07(5)(a)6 excludes repayments only when used for the
        # separate Wisconsin claim of right credit, which is not modeled.
        # Section 1341 deductions are not miscellaneous deductions under
        # IRC 67(b)(9), so paragraph 7 does not exclude them either.
        # Form 1 instructions exclude mortgage insurance premiums treated
        # as interest from the itemized deduction credit.
        wi_itmded = tax_unit("itemized_deductions_less_salt", period) - tax_unit(
            "deductible_mortgage_insurance_premiums", period
        )
        wi_stdded = tax_unit("wi_standard_deduction", period)
        excess_itmded = max_(0, wi_itmded - wi_stdded)
        p = parameters(period).gov.states.wi.tax.income
        return excess_itmded * p.credits.itemized_deduction.rate
