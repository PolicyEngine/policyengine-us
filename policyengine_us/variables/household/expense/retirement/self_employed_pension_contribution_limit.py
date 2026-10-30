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
        "limit becomes half of it less elective deferrals. The modeled input "
        "does not say which kind of plan the person has, so the limit is the "
        "most any of them allows: a profit-sharing plan with a 401(k) "
        "arrangement into which the person defers all of the elective "
        "deferral room that deferrals to other employers' plans leave. With "
        "no room left, it is the SEP and profit-sharing limit. Catch-up "
        "contributions sit outside the dollar limit, and the total never "
        "exceeds earned income. Defined benefit plans are not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/404#a_3_A_i_I",
        "https://www.law.cornell.edu/uscode/text/26/404#a_8_C",
        "https://www.law.cornell.edu/uscode/text/26/404#n",
        "https://www.law.cornell.edu/uscode/text/26/415#c_1",
        "https://www.law.cornell.edu/uscode/text/26/415#c_3_B",
        "https://www.law.cornell.edu/uscode/text/26/414#v_3_A",
        "https://www.irs.gov/pub/irs-pdf/p560.pdf#page=39",
        "https://www.irs.gov/pub/irs-prior/p560--2022.pdf#page=34",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.gross_income.retirement_contributions.limit
        # Step 3: earned income before the plan deduction.
        earned_income = person("self_employed_pension_earned_income", period)
        # Steps 4 and 5: the employer contribution rate, reduced because
        # compensation is net of the contribution. Steps 6 and 7 cap the rate
        # at the section 401(a)(17) compensation limit, which never binds:
        # 25% of it has exceeded the step 8 dollar limit in every year.
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
        # Steps 10 to 15: employer contributions and regular deferrals
        # together stay within the dollar limit (step 8) and within
        # compensation, which also excludes the employer contribution
        # (step 12).
        annual_additions = min_(
            min_(p.annual_additions, employer_limit + regular_deferral_room),
            (earned_income + regular_deferral_room) / 2,
        )
        # Steps 16 to 19: catch-up contributions, outside the dollar limit.
        # The total never exceeds earned income.
        return min_(earned_income, annual_additions + catch_up_room)
