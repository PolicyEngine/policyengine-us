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
        "attributable to it (lines 9 and 10). With the retirement plan under "
        "one named business (self_employed_pension_plan_business), all of "
        "that plan deduction is attributable to that business. By default "
        "each business with a net profit has a retirement plan, and the person "
        "chooses how much to contribute to each. Form 7206 gives no rule for "
        "that split, so the model takes the split that leaves the most earned "
        "income for the health insurance deduction: the plans under the other "
        "businesses carry as much of the plan deduction as they can. As in the "
        "plan limit, the model treats all of the plans as one employer's, so "
        "the worksheet limits apply to the plans together and each plan can "
        "carry up to its own business's earned income. The plan deduction "
        "attributable to a business is then the part of it above the other "
        "businesses' earned income. A partnership that the person doesn't "
        "control is a separate employer whose plan has limits of its own, and "
        "for its partners line 9 can exceed the model's. Each kind of "
        "business is one total per person: all "
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
        # Subsections (a)(3)(A)(iv), (h)(2) and (a)(8)(C): one employer's
        # profit-sharing trusts count as one trust, a SEP's deduction counts
        # against their limit, and each plan's contributions stay within its
        # own business's earned income.
        "https://www.law.cornell.edu/uscode/text/26/404",
        # Subsection (f)(1)(B): one employer's defined contribution plans
        # count as one plan.
        "https://www.law.cornell.edu/uscode/text/26/415#f_1_B",
        # PDF pages 7, 10: a sole proprietor is their own employer and a
        # partnership is each partner's, and the plans one employer maintains
        # count together.
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=7",
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


def plan_deduction_attributable_to_business(plan_deduction, other_earned_income):
    """Least part of the plan deduction that one business's plan must carry.

    Every business with a net profit has a retirement plan, the person
    chooses how much to contribute to each, and the plans under the other
    businesses have other_earned_income in all. The model treats the plans
    as one employer's, which a sole proprietor is for all of their own
    businesses. One employer's defined contribution plans count as one plan
    for the section 415(c) limits (415(f)(1)(B)), and its profit-sharing
    trusts as one trust for the section 404(a)(3) limit (404(a)(3)(A)(iv)),
    against which a SEP's deduction also counts (404(h)(2)), so the Pub. 560
    worksheet limits apply to the plans together. The only
    limit on each plan alone is its own business's earned income before the
    plan deduction (404(a)(8)(C)). So the other plans can carry the plan
    deduction up to their earned income, and this business's plan carries
    the rest (Form 7206 line 9).
    """
    return max_(0, plan_deduction - other_earned_income)


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
    # Line 5: net profits of every business whose earnings are subject to
    # self-employment tax, leaving out net losses.
    all_business_profits = (
        schedule_c_profit + farm_profit + partnership_profit + other_line_5_profits
    )
    # Lines 6 and 7: each business takes the deductible part of
    # self-employment tax (Schedule 1 line 15) in proportion to its share
    # of line 5.
    self_employment_tax_deduction = person("self_employment_tax_ald_person", period)

    def attributable_self_employment_tax_deduction(profit):
        share = np.divide(
            profit,
            all_business_profits,
            out=np.zeros_like(all_business_profits),
            where=all_business_profits > 0,
        )
        return self_employment_tax_deduction * share

    # Line 8 for each self-employment business.
    schedule_c_line_8 = schedule_c_profit - attributable_self_employment_tax_deduction(
        schedule_c_profit
    )
    farm_line_8 = farm_profit - attributable_self_employment_tax_deduction(farm_profit)
    partnership_line_8 = partnership_profit - (
        attributable_self_employment_tax_deduction(partnership_profit)
    )
    # Line 9: the SEP, SIMPLE and qualified plan deduction (Schedule 1 line
    # 16) attributable to each business.
    retirement_plan_deduction = person(
        "self_employed_pension_contribution_ald_person", period
    )
    retirement_plan_business = person("self_employed_pension_plan_business", period)
    retirement_plan_businesses = retirement_plan_business.possible_values

    def line_9(other_businesses_line_8, business):
        # A retirement plan under one named business: all of line 16.
        named = where(
            retirement_plan_business == business, retirement_plan_deduction, 0
        )
        # Plans under every business with a net profit, whose line 8 amounts
        # are their earned income (Pub. 560 Deduction Worksheet step 3): the
        # least that this business's plan must carry.
        least = plan_deduction_attributable_to_business(
            retirement_plan_deduction, other_businesses_line_8
        )
        return where(
            retirement_plan_business == retirement_plan_businesses.ALL, least, named
        )

    # Line 10 for each self-employment business.
    schedule_c = max_(
        0,
        schedule_c_line_8
        - line_9(
            farm_line_8 + partnership_line_8,
            retirement_plan_businesses.SCHEDULE_C,
        ),
    )
    farm = max_(
        0,
        farm_line_8
        - line_9(
            schedule_c_line_8 + partnership_line_8,
            retirement_plan_businesses.SCHEDULE_F,
        ),
    )
    partnership = max_(
        0,
        partnership_line_8
        - line_9(
            schedule_c_line_8 + farm_line_8,
            retirement_plan_businesses.PARTNERSHIP,
        ),
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
