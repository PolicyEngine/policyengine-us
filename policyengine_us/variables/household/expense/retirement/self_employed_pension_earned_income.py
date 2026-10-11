from policyengine_us.model_api import *


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
        "net profits, as on Form 7206 lines 5 to 8."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/401#c_2_A",
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        "https://www.irs.gov/pub/irs-pdf/p560.pdf#page=39",
        "https://www.irs.gov/pub/irs-prior/p560--2022.pdf#page=34",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
    )

    def formula(person, period, parameters):
        # Step 1: net profit from the business with the plan.
        plan_business_profit = max_(0, person("total_self_employment_income", period))
        # Net profits of every business whose earnings are subject to
        # self-employment tax, leaving out net losses.
        other_business_profits = max_(
            0, person("farm_operations_income", period)
        ) + max_(0, person("partnership_self_employment_net_earnings", period))
        all_business_profits = plan_business_profit + other_business_profits
        plan_business_share = np.divide(
            plan_business_profit,
            all_business_profits,
            out=np.zeros_like(all_business_profits),
            where=all_business_profits > 0,
        )
        # Step 2: the deductible part of self-employment tax (Schedule 1
        # line 15) attributable to the plan's business.
        self_employment_tax_deduction = (
            person("self_employment_tax_ald_person", period) * plan_business_share
        )
        # Step 3.
        return max_(0, plan_business_profit - self_employment_tax_deduction)
