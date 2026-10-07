from policyengine_us.model_api import *


def charitable_deduction_given_contribution_base(
    tax_unit, period, parameters, contribution_base
):
    """Itemized charitable deduction under 26 USC 170(b) for a given contribution base.

    The federal deduction uses positive federal adjusted gross income as the
    contribution base. States that measure the section 170(b) percentage
    limits and floor against their own adjusted gross income pass that
    instead.
    """
    # TODO: 26 USC 170(b)(1) defines 4 contribution categories with
    # separate AGI caps:
    #   (G) Cash to 50% limit orgs: 60% AGI (post-TCJA)
    #   (B) Cash to non-50% limit orgs: 30% AGI
    #   (C) Capital gain property to 50% limit orgs: 30% AGI
    #       (or 50% with basis-reduction election)
    #   (D) Capital gain property to non-50% limit orgs: 20% AGI
    # Currently we model two non-cash categories (50% vs 30% cap)
    # and treat all cash as subject to the overall cap only.
    # The cash split and the 20% category are not yet modeled.
    cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
    non_cash_donations = add(tax_unit, period, ["charitable_non_cash_donations"])
    non_cash_to_non_50_pct = add(
        tax_unit,
        period,
        ["charitable_non_cash_donations_non_50_pct_orgs"],
    )
    non_cash_to_50_pct = non_cash_donations - non_cash_to_non_50_pct
    p = parameters(period).gov.irs.deductions.itemized.charity

    # Non-cash to 50% limit orgs capped at 50% of AGI.
    # Note: this models the basis-reduction election under
    # 170(b)(1)(C)(iii); the default cap for capital gain
    # property is 30% per 170(b)(1)(C)(i).
    capped_non_cash_50 = min_(
        non_cash_to_50_pct, p.ceiling.non_cash * contribution_base
    )
    # Non-cash to non-50% limit orgs capped at 30% of AGI
    # per 170(b)(1)(B). Note: the stricter 20% cap for
    # capital gain property under 170(b)(1)(D) is not yet
    # modeled separately.
    capped_non_cash_non_50 = min_(
        non_cash_to_non_50_pct,
        p.ceiling.non_cash_to_non_50_pct_org * contribution_base,
    )
    capped_non_cash = capped_non_cash_50 + capped_non_cash_non_50

    total_cap = p.ceiling.all * contribution_base
    if p.floor.applies:
        deduction_floor = p.floor.amount * contribution_base
        reduced_non_cash_50 = max_(non_cash_to_50_pct - deduction_floor, 0)
        capped_reduced_non_cash_50 = min_(
            reduced_non_cash_50,
            p.ceiling.non_cash * contribution_base,
        )

        remaining_floor_after_50 = max_(deduction_floor - non_cash_to_50_pct, 0)
        reduced_non_cash_non_50 = max_(
            non_cash_to_non_50_pct - remaining_floor_after_50, 0
        )
        capped_reduced_non_cash_non_50 = min_(
            reduced_non_cash_non_50,
            p.ceiling.non_cash_to_non_50_pct_org * contribution_base,
        )

        remaining_floor = max_(remaining_floor_after_50 - non_cash_to_non_50_pct, 0)
        reduced_cash_donations = max_(cash_donations - remaining_floor, 0)
        return min_(
            capped_reduced_non_cash_50
            + capped_reduced_non_cash_non_50
            + reduced_cash_donations,
            total_cap,
        )
    return min_(capped_non_cash + cash_donations, total_cap)
