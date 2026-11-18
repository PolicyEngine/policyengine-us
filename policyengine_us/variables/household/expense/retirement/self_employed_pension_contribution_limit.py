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
        "limits it only by the section 402(g) or 415 limit. Defined "
        "benefit plans are not modeled, so contributions to them above this "
        "limit are cut."
    )
    definition_period = YEAR
    reference = (
        # Subsections (a)(3)(A)(i)(I), (a)(8)(C) and (D), (a)(10), (h)(1)(C)
        # and (n).
        "https://www.law.cornell.edu/uscode/text/26/404",
        # Subsections (a)(2), (c)(1) and (c)(3)(B) and (D).
        "https://www.law.cornell.edu/uscode/text/26/415",
        # Subsections (v)(2)(A) and (v)(3)(A).
        "https://www.law.cornell.edu/uscode/text/26/414#v",
        # PDF pages 15, 39: SIMPLE IRA compensation and the worksheet.
        "https://www.irs.gov/pub/irs-prior/p560--2025.pdf#page=15",
        "https://www.irs.gov/pub/irs-prior/p560--2022.pdf#page=34",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions.limit
        # Step 3: earned income before the plan deduction.
        earned_income = person("self_employed_pension_earned_income", period)
        # Steps 4 and 5: the employer contribution rate, reduced because
        # compensation is net of the contribution. Steps 6 and 7 cap the
        # employer contribution at the plan rate times the section
        # 401(a)(17) compensation limit. At current law that never binds the
        # result, because 25% of the compensation limit is 1.25 times the
        # step 8 dollar limit, so the model leaves it out; a reform that set
        # the rate times that limit below the dollar limit would need it.
        rate = p.profit_sharing_deduction_rate
        employer_limit = earned_income * rate / (1 + rate)
        # Step 9: elective deferrals, up to the section 402(g) room left
        # after deferrals to other employers' plans, which use the regular
        # limit before the catch-up amount.
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
        deferral_room = max_(
            0, person("elective_deferral_limit", period) - other_deferrals
        )
        catch_up_room = min_(deferral_room, person("k401_catch_up_limit", period))
        regular_deferral_room = deferral_room - catch_up_room
        # Steps 10 to 15: employer contributions stay within step 7 and
        # within half of what is left of earned income after the regular
        # deferrals (step 12), because compensation also excludes the
        # employer contribution. With the regular deferrals, they stay
        # within the dollar limit (step 8).
        annual_additions = min_(
            min_(p.annual_additions, employer_limit + regular_deferral_room),
            (earned_income + regular_deferral_room) / 2,
        )
        # Steps 16 to 19: catch-up contributions, outside the dollar limit.
        # The total never exceeds earned income.
        return min_(earned_income, annual_additions + catch_up_room)
