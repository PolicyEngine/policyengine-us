from policyengine_us.model_api import *


def compute_charitable_deduction(
    cash_50,
    cash_non_50,
    ordinary_50,
    ordinary_non_50,
    cg_50,
    cg_non_50,
    positive_agi,
    ceiling_all,
    ceiling_non_cash,
    ceiling_non_50,
    ceiling_cg_50,
    ceiling_cg_non_50,
    non_50_pct_cash_add_back=0.0,
    qualified_cash_election=False,
):
    agi = positive_agi
    limit_50 = ceiling_non_cash * agi
    limit_30_non_50 = ceiling_non_50 * agi
    limit_30_cg_50 = ceiling_cg_50 * agi
    limit_20_cg_non_50 = ceiling_cg_non_50 * agi

    if qualified_cash_election:
        # Under CARES Act § 2205(a) / P.L. 116-260 div. EE § 213, elected qualified cash
        # contributions to 50% orgs are disregarded when applying percentage limits to
        # other contributions, and then allowed up to remaining AGI (Pub 526 (2020) Worksheet 2).
        other_allowed = compute_charitable_deduction(
            cash_50=0,
            cash_non_50=cash_non_50,
            ordinary_50=ordinary_50,
            ordinary_non_50=ordinary_non_50,
            cg_50=cg_50,
            cg_non_50=cg_non_50,
            positive_agi=positive_agi,
            ceiling_all=ceiling_all,
            ceiling_non_cash=ceiling_non_cash,
            ceiling_non_50=ceiling_non_50,
            ceiling_cg_50=ceiling_cg_50,
            ceiling_cg_non_50=ceiling_cg_non_50,
            non_50_pct_cash_add_back=non_50_pct_cash_add_back,
            qualified_cash_election=False,
        )
        deductible_cash_50 = min_(
            cash_50, max_(0, ceiling_all * positive_agi - other_allowed)
        )
        return other_allowed + deductible_cash_50

    # Standard IRS Pub 526 Worksheet 2 sequential calculation:
    # Note: (G)(i) ordering: cash is taken into account first per
    # unrepealed (G)(iii)(II) and current IRS Worksheet 2.
    # 1. Cash contributions subject to limit based on 60% of AGI (Worksheet 2 lines 12-14, IRC § 170(b)(1)(G)):
    cash_ceiling = ceiling_all * agi
    deductible_cash_50 = min_(cash_50, cash_ceiling)

    # 2. Non-cash ordinary contributions subject to limit based on 50% of AGI (Worksheet 2 lines 15-18, IRC § 170(b)(1)(A)):
    room_for_ord_50 = max_(0, limit_50 - deductible_cash_50)
    deductible_ord_50 = min_(ordinary_50, room_for_ord_50)

    # 3. Contributions (other than capital gain property) subject to 30% limit (Worksheet 2 lines 19-25, IRC § 170(b)(1)(B)):
    # From 2026, P.L. 119-21 § 70425 adds back up to 10% of AGI of cash to 50% orgs:
    allowable_50_gifts = min_(cg_50 + ordinary_50, room_for_ord_50)
    subtracted_cash_50 = deductible_cash_50 - min_(
        deductible_cash_50, non_50_pct_cash_add_back * agi
    )
    room_under_50_for_non_50 = max_(
        0, limit_50 - (allowable_50_gifts + subtracted_cash_50)
    )
    non_50_ordinary_and_cash = cash_non_50 + ordinary_non_50
    deductible_non_50_ordinary = min_(
        non_50_ordinary_and_cash,
        min_(limit_30_non_50, room_under_50_for_non_50),
    )

    # 4. Contributions of capital gain property to 50% limit orgs subject to 30% limit (Worksheet 2 lines 26-31, IRC § 170(b)(1)(C)):
    contribs_ord_and_cash_to_50 = ordinary_50 + cash_50
    room_under_50_for_cg_50 = max_(0, limit_50 - contribs_ord_and_cash_to_50)
    deductible_cg_50 = min_(
        cg_50,
        min_(limit_30_cg_50, room_under_50_for_cg_50),
    )

    # 5. Contributions of capital gain property to non-50% limit orgs subject to 20% limit (Worksheet 2 lines 32-41, IRC § 170(b)(1)(D)):
    deductible_so_far = (
        subtracted_cash_50
        + deductible_ord_50
        + deductible_non_50_ordinary
        + deductible_cg_50
    )
    room_under_50_overall = max_(0, limit_50 - deductible_so_far)
    room_under_30_after_non_50_ord = max_(
        0, limit_30_non_50 - deductible_non_50_ordinary
    )
    room_under_30_after_cg_50 = max_(0, limit_30_non_50 - deductible_cg_50)
    deductible_cg_non_50 = min_(
        cg_non_50,
        min_(
            limit_20_cg_non_50,
            min_(
                room_under_50_overall,
                min_(
                    room_under_30_after_non_50_ord,
                    room_under_30_after_cg_50,
                ),
            ),
        ),
    )

    # Total deductible contributions before floor (Worksheet 2 line 52):
    return (
        deductible_cash_50
        + deductible_ord_50
        + deductible_non_50_ordinary
        + deductible_cg_50
        + deductible_cg_non_50
    )


class charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction"
    unit = USD
    documentation = "Deduction from taxable income for charitable donations."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        # 26 U.S. Code § 170(b)(1) defines charitable deduction limits and their
        # interactions, calculated sequentially per IRS Publication 526, Worksheet 2:
        #   (G) Cash to 50% limit orgs: 60% AGI (post-TCJA; 50% pre-2018; 100% 2020-2021)
        #   (A) Non-cash ordinary / non-capital-gain to 50% limit orgs: 50% AGI
        #   (B) Cash & non-cash ordinary to non-50% limit orgs: 30% AGI (reduced by 50% gifts)
        #   (C) Capital gain property to 50% limit orgs: 30% AGI (reduced by ordinary 50% gifts)
        #   (D) Capital gain property to non-50% limit orgs: 20% AGI (taken into account last)
        cash_50 = add(tax_unit, period, ["resolved_charitable_cash_donations_50_pct"])
        cash_non_50 = add(
            tax_unit, period, ["resolved_charitable_cash_donations_non_50_pct"]
        )
        ordinary_50 = add(
            tax_unit, period, ["resolved_charitable_non_cash_donations_50_pct"]
        )
        ordinary_non_50 = add(
            tax_unit,
            period,
            ["resolved_charitable_non_cash_donations_non_50_pct"],
        )
        cg_50 = add(
            tax_unit,
            period,
            ["resolved_charitable_capital_gain_donations_50_pct"],
        )
        cg_non_50 = add(
            tax_unit,
            period,
            ["resolved_charitable_capital_gain_donations_non_50_pct"],
        )

        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity

        total_allowed = compute_charitable_deduction(
            cash_50=cash_50,
            cash_non_50=cash_non_50,
            ordinary_50=ordinary_50,
            ordinary_non_50=ordinary_non_50,
            cg_50=cg_50,
            cg_non_50=cg_non_50,
            positive_agi=positive_agi,
            ceiling_all=p.ceiling.all,
            ceiling_non_cash=p.ceiling.non_cash,
            ceiling_non_50=p.ceiling.non_cash_to_non_50_pct_org,
            ceiling_cg_50=p.ceiling.capital_gain_to_50_pct_org,
            ceiling_cg_non_50=p.ceiling.capital_gain_to_non_50_pct_org,
            non_50_pct_cash_add_back=p.ceiling.non_50_pct_cash_add_back,
            qualified_cash_election=p.qualified_cash_election,
        )

        # 2026+ floor under IRC § 170(b)(1)(I) (P.L. 119-21):
        # Applies to contributions otherwise allowable (after ceilings).
        if p.floor.applies:
            deduction_floor = p.floor.amount * positive_agi
            return max_(0, total_allowed - deduction_floor)

        return total_allowed
