from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.retirement.self_employed_pension_contribution_limit import (
    elective_deferral_room,
)


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
        "businesses carry as much of the plan deduction as they can. Each plan "
        "can carry up to its own business's earned income. Elective deferrals "
        "can sit in any of the plans, within the person's one section 402(g) "
        "limit and catch-up amount. Employer contributions stay within each "
        "employer's deduction "
        "limit, the reduced plan rate (20% at the 25% rate) times the earned "
        "income of the businesses whose plans that employer maintains. The "
        "person is the employer for their own Schedule C business and farm, "
        "whose plans share one limit, and a partnership is the employer of "
        "its partners, so its plan has a limit of its own. The model figures "
        "that limit from the person's own earned income from the "
        "partnership, as the Pub. 560 worksheet does, leaving out other "
        "participants' compensation. As in the plan "
        "limit, the dollar limit and the limit of half of earned income less "
        "deferrals apply to all of the plans together, as section 415 applies "
        "them when the person controls more than 50 percent of the "
        "partnership. When the person doesn't, the law gives the "
        "partnership's plan its own such limits, which can raise line 9; the "
        "model has no data on ownership shares. The plan deduction "
        "attributable to a business is then "
        "the part of it above what the other plans can carry. Each kind of "
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
        # Subsections (a)(3)(A)(i)(I) and (iv), (a)(8), (a)(12), (h)(2) and
        # (n): the 25% limit on an employer's contributions, with one
        # employer's profit-sharing trusts as one trust and a SEP's deduction
        # counted against it; the employer of a self-employed person (the
        # person treated as such under 401(c)(4)) and their compensation,
        # earned income from the plan's business; each plan's contributions
        # within that earned income; and elective deferrals outside the
        # limit.
        "https://www.law.cornell.edu/uscode/text/26/404",
        # Subsections (f)(1)(B) and (h): one employer's defined contribution
        # plans count as one plan, and so do those of businesses under more
        # than 50 percent common control (section 414(c)).
        "https://www.law.cornell.edu/uscode/text/26/415",
        "https://www.law.cornell.edu/uscode/text/26/414#c",
        # Subsection (g)(1)(A): one elective deferral limit for each
        # individual.
        "https://www.law.cornell.edu/uscode/text/26/402#g_1_A",
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
        return form_7206_line_13(person, period, parameters)


def plan_deduction_attributable_to_business(
    plan_deduction, other_earned_income, other_employer_room, deferral_room
):
    """Least part of the plan deduction that one business's plan must carry.

    Every business with a net profit has a retirement plan, and the person
    chooses how much to contribute to each. The plans under the other
    businesses have other_earned_income in all, and each plan's
    contributions stay within its own business's earned income before the
    plan deduction (404(a)(8)(C)).

    Elective deferrals sit outside an employer's deduction limit (404(n)),
    so the person can put them in any plan, within their one section 402(g)
    limit (402(g)(1)(A)) and catch-up amount (414(v)): deferral_room.
    Employer contributions stay within each employer's limit of 25% of
    compensation (404(a)(3)(A)(i)(I)), which for a self-employed person is
    earned income from the business whose plan it is, net of the employer
    contribution (404(a)(8)(D), 404(a)(12)): the reduced rate times earned
    income before the plan deduction (Pub. 560 steps 4 and 5). A sole
    proprietor is the employer for all of their own businesses (401(c)(4),
    404(a)(8)(A)), and their profit-sharing trusts count as one trust for
    that limit (404(a)(3)(A)(iv)); a partnership is the employer of its
    partners, so its plan has a limit of its own. other_employer_room is what
    those limits leave for the other plans' employer contributions when this
    business's plan makes none. The model applies the dollar limit and the
    limit of half of earned income less deferrals to all of the plans
    together, as section 415 does for one employer (415(f)(1)(B)) or for
    businesses under more than 50 percent common control (414(c), 415(h)),
    and the plan deduction is within them.

    So the other plans can carry their employer room plus the person's
    deferral room, up to their earned income, and this business's plan
    carries the rest (Form 7206 line 9). Where that capacity passes the plan
    deduction, this plan carries none of it.
    """
    other_plans = min_(other_earned_income, other_employer_room + deferral_room)
    return max_(0, plan_deduction - other_plans)


def form_7206_line_13(person, period, parameters, other_line_5_profits=0):
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
    # With plans under every business with a net profit, their line 8
    # amounts are their earned income (Pub. 560 Deduction Worksheet step 3).
    # Each employer's limit on employer contributions: the reduced plan rate
    # (steps 4 and 5) times the earned income of the businesses whose plans
    # it maintains. The person is the employer for their own Schedule C
    # business and farm, and a partnership for its partners.
    rate = parameters(
        period
    ).gov.irs.gross_income.retirement_contributions.limit.profit_sharing_deduction_rate
    reduced_rate = rate / (1 + rate)
    own_businesses_employer_room = reduced_rate * (schedule_c_line_8 + farm_line_8)
    partnership_employer_room = reduced_rate * partnership_line_8
    # Elective deferrals can sit in any of the plans.
    deferral_room = elective_deferral_room(person, period)

    def line_9(other_businesses_line_8, other_businesses_employer_room, business):
        # A retirement plan under one named business: all of line 16.
        named = where(
            retirement_plan_business == business, retirement_plan_deduction, 0
        )
        # Plans under every business with a net profit: the least that this
        # business's plan must carry.
        least = plan_deduction_attributable_to_business(
            retirement_plan_deduction,
            other_businesses_line_8,
            other_businesses_employer_room,
            deferral_room,
        )
        return where(
            retirement_plan_business == retirement_plan_businesses.ALL, least, named
        )

    # Line 10 for each self-employment business. The plan under the person's
    # other business can take all of their employer room, up to that
    # business's earned income, when this business's plan makes no employer
    # contribution.
    schedule_c = max_(
        0,
        schedule_c_line_8
        - line_9(
            farm_line_8 + partnership_line_8,
            min_(farm_line_8, own_businesses_employer_room) + partnership_employer_room,
            retirement_plan_businesses.SCHEDULE_C,
        ),
    )
    farm = max_(
        0,
        farm_line_8
        - line_9(
            schedule_c_line_8 + partnership_line_8,
            min_(schedule_c_line_8, own_businesses_employer_room)
            + partnership_employer_room,
            retirement_plan_businesses.SCHEDULE_F,
        ),
    )
    partnership = max_(
        0,
        partnership_line_8
        - line_9(
            schedule_c_line_8 + farm_line_8,
            own_businesses_employer_room,
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
