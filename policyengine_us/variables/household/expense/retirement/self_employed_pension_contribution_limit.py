from policyengine_us.model_api import *


class self_employed_pension_contribution_limit(Variable):
    value_type = float
    entity = Person
    label = "Self-employed retirement plan contribution limit"
    unit = USD
    documentation = (
        "Largest deduction for the person's own SEP, SIMPLE and qualified "
        "defined contribution plan contributions (Schedule 1 line 16), from "
        "the Pub. 560 Deduction Worksheet for Self-Employed. Plan "
        "compensation for a self-employed person is earned income net of "
        "the plan deduction itself, so the 25% employer rate becomes 20% of "
        "earned income before that deduction, and the 100%-of-compensation "
        "limit caps employer contributions at half of what is left of "
        "earned income after elective deferrals (step 12). The modeled input "
        "does not say which kind of plan the person has, so the limit is the "
        "most a SEP or a qualified defined contribution plan allows: a "
        "profit-sharing plan with a 401(k) arrangement into which the person "
        "defers, before tax, all of the elective deferral room that "
        "deferrals to other employers' 401(k) and 403(b) plans leave. With no "
        "room left, it is the SEP and profit-sharing limit. Catch-up "
        "contributions sit outside the dollar limit, and the total never "
        "exceeds earned income. A SEP allows less, so the limit overstates "
        "its deductions. A SIMPLE IRA usually allows less too, but the "
        "contributions don't reduce its compensation, and section 415 "
        "doesn't apply to it. So when deferrals to other employers' plans "
        "leave elective deferral room close to earned income, a SIMPLE IRA "
        "can allow slightly more. A self-employed minister's section "
        "403(b)(9) account can also allow more, since section 404(a)(10) "
        "limits it only by the section 402(g) or 415 limit. Earned income "
        "comes from every business under which a plan is established "
        "(self_employed_pension_earned_income), under one dollar limit and "
        "one elective deferral limit. A sole proprietor is the employer for "
        "all of their own businesses, so their plans share one dollar limit. "
        "A partnership is a separate employer, and unless it is under common "
        "control with the person's own business, its plan has a dollar limit "
        "of its own. The model applies a single dollar limit to all of them, "
        "which understates the limit only when that dollar limit binds. "
        "Defined benefit plans are not modeled, so contributions to them "
        "above this limit are cut."
    )
    definition_period = YEAR
    reference = (
        # Subsections (a)(3)(A)(i)(I), (a)(8)(C) and (D), (a)(10), (h)(1)(C)
        # and (n).
        "https://www.law.cornell.edu/uscode/text/26/404",
        # Subsections (a)(2), (c)(1), (c)(3)(B) and (D), (f)(1)(B) and (h):
        # section 415 aggregates the plans of one employer.
        "https://www.law.cornell.edu/uscode/text/26/415",
        # Subsections (c), (v)(2)(A) and (v)(3)(A): employers under common
        # control are one employer.
        "https://www.law.cornell.edu/uscode/text/26/414",
        # PDF pages 7, 15, 39: the employer and compensation of a
        # self-employed person, SIMPLE IRA compensation, and the worksheet.
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=7",
        "https://www.irs.gov/pub/irs-prior/p560--2022.pdf#page=34",
    )

    def formula(person, period, parameters):
        # Step 3: earned income before the plan deduction.
        earned_income = person("self_employed_pension_earned_income", period)
        return self_employed_plan_limit(
            earned_income, *self_employed_plan_room(person, period, parameters)
        )


def self_employed_plan_room(person, period, parameters):
    """The limits every plan of a self-employed person shares.

    Returns the employer contribution rate (Pub. 560 Deduction Worksheet for
    Self-Employed, step 4), the section 415(c) dollar limit (step 8), and the
    regular and catch-up elective deferral room (steps 9 and 17).
    """
    p = parameters(period).gov.irs.gross_income.retirement_contributions.limit
    # Step 9: elective deferrals, up to the section 402(g) room left after
    # deferrals to other employers' plans, which use the regular limit
    # before the catch-up amount.
    other_deferrals = add(
        person,
        period,
        [
            "traditional_401k_contributions",
            "roth_401k_contributions",
            "traditional_403b_contributions",
            "roth_403b_contributions",
        ],
    )
    deferral_room = max_(0, person("elective_deferral_limit", period) - other_deferrals)
    catch_up_room = min_(deferral_room, person("k401_catch_up_limit", period))
    regular_deferral_room = deferral_room - catch_up_room
    return (
        p.profit_sharing_deduction_rate,
        p.annual_additions,
        regular_deferral_room,
        catch_up_room,
    )


def self_employed_plan_limit(
    earned_income, rate, dollar_limit, regular_deferral_room, catch_up_room
):
    """Pub. 560 Deduction Worksheet for Self-Employed, steps 4 to 19.

    The largest plan deduction for earned income figured before that
    deduction (step 3), with the rate, dollar limit and deferral room from
    self_employed_plan_room.
    """
    # Steps 4 and 5: the employer contribution rate, reduced because
    # compensation is net of the contribution. Steps 6 and 7 cap the
    # employer contribution at the plan rate times the section 401(a)(17)
    # compensation limit. At current law that never binds the result,
    # because 25% of the compensation limit is 1.25 times the step 8 dollar
    # limit, so the model leaves it out; a reform that set the rate times
    # that limit below the dollar limit would need it.
    employer_limit = earned_income * rate / (1 + rate)
    # Steps 10 to 15: employer contributions stay within step 7 and within
    # half of what is left of earned income after the regular deferrals
    # (step 12), because compensation also excludes the employer
    # contribution. With the regular deferrals, they stay within the dollar
    # limit (step 8).
    annual_additions = min_(
        min_(dollar_limit, employer_limit + regular_deferral_room),
        (earned_income + regular_deferral_room) / 2,
    )
    # Steps 16 to 19: catch-up contributions, outside the dollar limit. The
    # total never exceeds earned income.
    return min_(earned_income, annual_additions + catch_up_room)


def plan_deduction_attributable_to_business(
    plan_deduction,
    earned_income,
    other_earned_income,
    rate,
    dollar_limit,
    regular_deferral_room,
    catch_up_room,
):
    """Least part of the plan deduction that one business's plan must carry.

    The person has a plan under this business, with earned_income, and plans
    under other businesses, with other_earned_income in all, and chooses how
    much to contribute to each. The plans share one dollar limit and one
    elective deferral limit, and each one stays within its own business's
    worksheet limits: employer contributions at most the reduced rate times
    its earned income (steps 4 and 5) and at most half of its earned income
    less its deferrals (step 12), and all contributions at most its earned
    income. The result is the share of plan_deduction left to this plan when
    the other plans carry as much of it as they can (Form 7206 line 9).
    """
    reduced_rate = rate / (1 + rate)
    other_limit = self_employed_plan_limit(
        other_earned_income,
        rate,
        dollar_limit,
        regular_deferral_room,
        catch_up_room,
    )
    # What the other plans cannot carry.
    excess = plan_deduction - other_limit
    # The room the other plans leave when they carry all they can. Below
    # their earned income, that takes every dollar of the deferral and
    # catch-up room. At their earned income, they contribute it with the
    # mix that leaves this plan the most: catch-up contributions up to the
    # reduced rate times their earned income, or as many as the other
    # limits require, and the fewest elective deferrals that step 12 allows.
    at_earned_income = other_limit >= other_earned_income
    least_catch_up = max_(
        max_(0, (other_earned_income - regular_deferral_room) / 2),
        max_(
            (1 - reduced_rate) * other_earned_income - regular_deferral_room,
            other_earned_income - dollar_limit,
        ),
    )
    other_catch_up = min_(
        catch_up_room,
        max_(least_catch_up, min_(catch_up_room, reduced_rate * other_earned_income)),
    )
    other_deferrals = where(
        other_catch_up < reduced_rate * other_earned_income,
        other_earned_income - 2 * other_catch_up,
        (1 - reduced_rate) * other_earned_income - other_catch_up,
    )
    room_left = self_employed_plan_limit(
        earned_income,
        rate,
        dollar_limit=max_(
            0,
            where(
                at_earned_income,
                dollar_limit - (other_earned_income - other_catch_up),
                dollar_limit - (other_limit - catch_up_room),
            ),
        ),
        regular_deferral_room=where(
            at_earned_income, max_(0, regular_deferral_room - other_deferrals), 0
        ),
        catch_up_room=where(
            at_earned_income, max_(0, catch_up_room - other_catch_up), 0
        ),
    )
    # Up to room_left, this plan carries just the excess. Beyond it, the
    # other plans make room only by trading elective deferrals for employer
    # contributions, which step 12 allows at 50 cents on the dollar: each
    # further dollar of the excess moves two dollars to this plan and takes
    # one from the others.
    return min_(plan_deduction, max_(0, max_(excess, 2 * excess - room_left)))
