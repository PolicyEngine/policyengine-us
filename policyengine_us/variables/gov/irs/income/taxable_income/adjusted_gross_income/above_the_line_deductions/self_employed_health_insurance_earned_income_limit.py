from policyengine_us.model_api import *


class self_employed_health_insurance_earned_income_limit(Variable):
    value_type = float
    entity = Person
    label = "Self-employed health insurance deduction earned income limit"
    unit = USD
    documentation = (
        "Earned income, within the meaning of 26 U.S.C. 401(c), from the "
        "business under which the health plan is established; the "
        "self-employed health insurance deduction cannot exceed it (Form "
        "7206 line 13). The model treats the person's Schedule C business as "
        "that business. Its net profit is reduced by the part of the "
        "deductible part of self-employment tax attributable to it (lines 5 "
        "to 7) and by the self-employed SEP, SIMPLE and qualified plan "
        "deduction (line 9), which the model also bases on Schedule C income. "
        "S corporation wages (line 11) are not modeled, and self-employment "
        "income inputs are already net of any section 911 exclusion (line 12)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_A",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2_A",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
        # The worksheet Form 7206 replaced, used before 2023.
        "https://www.irs.gov/pub/irs-prior/p535--2022.pdf#page=23",
        # The single-business worksheet in the Form 1040 instructions.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=89",
    )

    def formula(person, period, parameters):
        # Line 4: net profit from the business under which the plan is
        # established.
        plan_business_profit = max_(0, person("total_self_employment_income", period))
        # Line 5: net profits of every business whose earnings are subject to
        # self-employment tax, leaving out net losses.
        other_business_profits = max_(
            0, person("farm_operations_income", period)
        ) + max_(0, person("partnership_self_employment_net_earnings", period))
        all_business_profits = plan_business_profit + other_business_profits
        # Line 6: the plan business's share of those profits.
        plan_business_share = np.divide(
            plan_business_profit,
            all_business_profits,
            out=np.zeros_like(all_business_profits),
            where=all_business_profits > 0,
        )
        # Lines 7 and 8: the deductible part of self-employment tax
        # (Schedule 1 line 15) attributable to the plan business.
        self_employment_tax_deduction = (
            person("self_employment_tax_ald_person", period) * plan_business_share
        )
        # Lines 9 and 10: the SEP, SIMPLE and qualified plan deduction
        # (Schedule 1 line 16) for the plan business.
        retirement_plan_deduction = person(
            "self_employed_pension_contribution_ald_person", period
        )
        return max_(
            0,
            plan_business_profit
            - self_employment_tax_deduction
            - retirement_plan_deduction,
        )
