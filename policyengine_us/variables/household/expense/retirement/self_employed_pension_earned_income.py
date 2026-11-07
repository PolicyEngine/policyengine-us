from policyengine_us.model_api import *


class self_employed_pension_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Earned income for self-employed retirement plan limits"
    unit = USD
    documentation = (
        "Earned income, within the meaning of 26 U.S.C. 401(c)(2), from the "
        "business or businesses under which the self-employed SEP, SIMPLE or "
        "qualified plan is established, determined without regard to the plan "
        "deduction itself: net profit less the deductible part of "
        "self-employment tax (Pub. 560 Deduction Worksheet for Self-Employed, "
        "steps 1 to 3). The plan may be established under the Schedule C "
        "business, the Schedule F farm or a partnership that reports net "
        "earnings on Schedule K-1 box 14 code A "
        "(self_employed_pension_plan_business). By default every one of these "
        "businesses with a net profit has a plan, and their earned income is "
        "added up. The worksheet's step 2 enters all of Schedule 1 line 15; "
        "the model splits it by each business's share of the net profits, as "
        "on Form 7206 lines 5 to 8, so with every profitable business in the "
        "plan step 2 is all of line 15. All Schedule C profit counts as "
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
    """Pub. 560 step 3 for the businesses under which the plan is established.

    other_line_5_profits adds the profits of other businesses whose
    self-employment tax is in Schedule 1 line 15, such as the owners' draw
    reform's draw profits, so the plan businesses take only their share.
    """
    # Step 1: net profit of each business that can establish a plan,
    # leaving out net losses.
    schedule_c_profit = max_(0, person("total_self_employment_income", period))
    farm_profit = max_(0, person("farm_operations_income", period))
    partnership_profit = max_(
        0, person("partnership_self_employment_net_earnings", period)
    )
    plan_business = person("self_employed_pension_plan_business", period)
    businesses = plan_business.possible_values
    # ALL, the default, puts a plan under every one of them.
    plan_business_profit = select(
        [
            plan_business == businesses.SCHEDULE_C,
            plan_business == businesses.SCHEDULE_F,
            plan_business == businesses.PARTNERSHIP,
        ],
        [schedule_c_profit, farm_profit, partnership_profit],
        default=schedule_c_profit + farm_profit + partnership_profit,
    )
    # Net profits of every business whose earnings are subject to
    # self-employment tax.
    all_business_profits = (
        schedule_c_profit + farm_profit + partnership_profit + other_line_5_profits
    )
    plan_business_share = np.divide(
        plan_business_profit,
        all_business_profits,
        out=np.zeros_like(all_business_profits),
        where=all_business_profits > 0,
    )
    # Step 2: the deductible part of self-employment tax (Schedule 1
    # line 15) attributable to the plan's businesses.
    self_employment_tax_deduction = (
        person("self_employment_tax_ald_person", period) * plan_business_share
    )
    # Step 3.
    return max_(0, plan_business_profit - self_employment_tax_deduction)
