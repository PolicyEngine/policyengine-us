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
        "7206 line 13). The plan may be established under a Schedule C "
        "business, a Schedule F farm, a partnership that reports net earnings "
        "on Schedule K-1 box 14 code A, or an S corporation in which the "
        "person is a more-than-2% shareholder, and earned income from other "
        "businesses does not count. For each of the first three, earned income "
        "is net profit less the part of the deductible part of "
        "self-employment tax attributable to that business (lines 4 to 8) and "
        "less the self-employed SEP, SIMPLE and qualified plan deduction "
        "attributable to it (lines 9 and 10); the model bases that plan "
        "deduction on Schedule C income, so only the Schedule C business "
        "subtracts it. For an S corporation it is the shareholder's wages "
        "from the corporation (line 11). self_employed_health_insurance_plan_"
        "business names the business; when it is not supplied, the limit uses "
        "the business with the largest earned income, as one plan established "
        "under the person's most profitable business would. Self-employment "
        "income inputs are already net of any section 911 exclusion (line 12)."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/162#l_2_A",
        "https://www.law.cornell.edu/uscode/text/26/162#l_5",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2_A",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
        # Where a plan may be established, and one Form 7206 per plan.
        "https://www.irs.gov/pub/irs-prior/i7206--2023.pdf#page=1",
        # The worksheet Form 7206 replaced, used before 2023.
        "https://www.irs.gov/pub/irs-prior/p535--2022.pdf#page=23",
        # The single-business worksheet in the Form 1040 instructions.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=89",
    )

    def formula(person, period, parameters):
        # Line 4 for each business that can establish a plan: its net profit,
        # or a partner's net earnings from self-employment.
        schedule_c_profit = max_(0, person("total_self_employment_income", period))
        farm_profit = max_(0, person("farm_operations_income", period))
        partnership_profit = max_(
            0, person("partnership_self_employment_net_earnings", period)
        )
        # Line 5: net profits of every business whose earnings are subject to
        # self-employment tax, leaving out net losses.
        all_business_profits = schedule_c_profit + farm_profit + partnership_profit
        # Lines 6 and 7: each business takes the deductible part of
        # self-employment tax (Schedule 1 line 15) in proportion to its share
        # of line 5.
        self_employment_tax_deduction = person("self_employment_tax_ald_person", period)
        self_employment_tax_deduction_rate = np.divide(
            self_employment_tax_deduction,
            all_business_profits,
            out=np.zeros_like(all_business_profits),
            where=all_business_profits > 0,
        )
        # Lines 9 and 10: the SEP, SIMPLE and qualified plan deduction
        # (Schedule 1 line 16) is attributable to the Schedule C business.
        retirement_plan_deduction = person(
            "self_employed_pension_contribution_ald_person", period
        )
        # Line 10 for each self-employment business.
        schedule_c = max_(
            0,
            schedule_c_profit * (1 - self_employment_tax_deduction_rate)
            - retirement_plan_deduction,
        )
        farm = max_(0, farm_profit * (1 - self_employment_tax_deduction_rate))
        partnership = max_(
            0, partnership_profit * (1 - self_employment_tax_deduction_rate)
        )
        # Line 11: an S corporation shareholder's wages from the corporation.
        s_corporation = max_(0, person("s_corp_shareholder_medicare_wages", period))
        plan_business = person("self_employed_health_insurance_plan_business", period)
        businesses = plan_business.possible_values
        return select(
            [
                plan_business == businesses.SCHEDULE_C,
                plan_business == businesses.SCHEDULE_F,
                plan_business == businesses.PARTNERSHIP,
                plan_business == businesses.S_CORPORATION,
            ],
            [schedule_c, farm, partnership, s_corporation],
            # UNSPECIFIED: the business with the largest earned income.
            default=max_(max_(schedule_c, farm), max_(partnership, s_corporation)),
        )
