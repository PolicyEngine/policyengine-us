from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.adjusted_gross_income.above_the_line_deductions.self_employed_health_insurance_earned_income_limit import (
    form_7206_line_7,
)


class self_employed_pension_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Earned income for self-employed retirement plan limits"
    unit = USD
    documentation = (
        "Earned income, within the meaning of 26 U.S.C. 401(c)(2), from the "
        "business that maintains the self-employed SEP, SIMPLE or qualified "
        "plan, determined without regard to the plan deduction itself: net "
        "profit less the deductible part of self-employment tax (Pub. 560 "
        "Deduction Worksheet for Self-Employed, step 3). The model treats the "
        "person's Schedule C business as the plan's business. When the person "
        "also has farm or partnership self-employment earnings, the deductible "
        "part of self-employment tax is split by each business's share of the "
        "net profits, as on Form 7206 lines 5 to 8; the worksheet's step 2 "
        "enters all of Schedule 1 line 15. All Schedule C profit counts as "
        "earned income: the model assumes the personal-services test of "
        "section 401(c)(2)(A)(i) is met."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/401#c_2_A",
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        # PDF pages 7, 39
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/p560--2022.pdf#page=34",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
    )

    def formula(person, period, parameters):
        return pension_plan_earned_income(person, period)


def pension_plan_earned_income(person, period, other_line_5_profits=0):
    """Pub. 560 step 3 for the Schedule C plan business.

    other_line_5_profits adds the profits of other businesses whose
    self-employment tax is in Schedule 1 line 15, such as the owners' draw
    reform's draw profits, so the plan business takes only its share.
    """
    # Step 1: net profit from the business with the plan.
    plan_business_profit = max_(0, person("total_self_employment_income", period))
    # Step 2: the deductible part of self-employment tax (Schedule 1
    # line 15) attributable to the plan's business, split by net profit as
    # on Form 7206 lines 5 to 7.
    self_employment_tax_deduction = form_7206_line_7(
        person, period, plan_business_profit, other_line_5_profits
    )
    # Step 3.
    return max_(0, plan_business_profit - self_employment_tax_deduction)
