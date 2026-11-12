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
        "subtracts it. Each kind of business is one total per person: all "
        "Schedule C income (SSTB and non-SSTB), all Schedule F profit, all "
        "K-1 box 14 code A earnings and all more-than-2% shareholder wages, "
        "so a loss in one business of a kind reduces line 4. Schedule 1 line "
        "15 is read per person: each person's own deductible self-employment "
        "tax. For an S corporation it is the shareholder's wages from the "
        "corporation (line 11). self_employed_health_insurance_plan_business "
        "names the business; when it is not supplied, the limit uses the "
        "business with the largest earned income, the most that one plan can "
        "deduct. Conservation Reserve Program payments, the optional methods "
        "of figuring net earnings and the personal-services test of section "
        "401(c)(2)(A)(i) are not modeled, so each business's net profit enters "
        "lines 4 and 5 in full. Self-employment income inputs are already net "
        "of any section 911 exclusion (line 12)."
    )
    definition_period = YEAR
    reference = (
        # Subsection (l)(2)(A), and (l)(5) for S corporation shareholders.
        "https://www.law.cornell.edu/uscode/text/26/162#l",
        "https://www.law.cornell.edu/uscode/text/26/401#c_2_A",
        "https://www.irs.gov/pub/irs-prior/f7206--2023.pdf#page=1",
        # Where a plan may be established, and one Form 7206 per plan.
        # PDF pages 1-2
        "https://www.irs.gov/pub/irs-prior/i7206--2023.pdf#page=1",
        # The worksheet Form 7206 replaced, used before 2023.
        "https://www.irs.gov/pub/irs-prior/p535--2022.pdf#page=23",
        # The single-business worksheet in the Form 1040 instructions.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2022.pdf#page=89",
    )

    def formula(person, period, parameters):
        return form_7206_line_13(person, period)


def form_7206_line_7(person, period, line_4, other_line_5_profits=0):
    """Form 7206 line 7 for a business whose line 4 profit is line_4.

    The part of the deductible part of self-employment tax (Schedule 1 line
    15) attributable to the business. The self-employed retirement plan
    limit uses the same split for its earned income (Pub. 560 step 2).
    other_line_5_profits adds the profits of businesses that cannot
    establish the plan but whose self-employment tax is in Schedule 1 line
    15, such as the owners' draw reform's draw profits.
    """
    # Line 5: net profits of every business whose earnings are subject to
    # self-employment tax, leaving out net losses.
    line_5 = (
        max_(0, person("total_self_employment_income", period))
        + max_(0, person("farm_operations_income", period))
        + max_(0, person("partnership_self_employment_net_earnings", period))
        + other_line_5_profits
    )
    # Line 6: the business's share of line 5.
    line_6 = np.divide(
        line_4,
        line_5,
        out=np.zeros_like(line_5),
        where=line_5 > 0,
    )
    # Line 7: that share of Schedule 1 line 15.
    return person("self_employment_tax_ald_person", period) * line_6


def form_7206_line_13(person, period, other_line_5_profits=0):
    """Form 7206 line 13 for the plan business.

    other_line_5_profits adds the profits of businesses that cannot
    establish the plan here but whose self-employment tax is in Schedule 1
    line 15, such as the owners' draw reform's draw profits.
    """
    # Line 4 for each business that can establish a plan: its net profit,
    # or a partner's net earnings from self-employment.
    schedule_c_profit = max_(0, person("total_self_employment_income", period))
    farm_profit = max_(0, person("farm_operations_income", period))
    partnership_profit = max_(
        0, person("partnership_self_employment_net_earnings", period)
    )

    # Lines 5 to 7: each business takes the deductible part of
    # self-employment tax (Schedule 1 line 15) in proportion to its share
    # of the net profits of every business subject to self-employment tax.
    def attributable_self_employment_tax_deduction(profit):
        return form_7206_line_7(person, period, profit, other_line_5_profits)

    # Lines 9 and 10: the SEP, SIMPLE and qualified plan deduction
    # (Schedule 1 line 16) is attributable to the Schedule C business.
    retirement_plan_deduction = person(
        "self_employed_pension_contribution_ald_person", period
    )
    # Line 10 for each self-employment business.
    schedule_c = max_(
        0,
        schedule_c_profit
        - attributable_self_employment_tax_deduction(schedule_c_profit)
        - retirement_plan_deduction,
    )
    farm = max_(
        0, farm_profit - attributable_self_employment_tax_deduction(farm_profit)
    )
    partnership = max_(
        0,
        partnership_profit
        - attributable_self_employment_tax_deduction(partnership_profit),
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
