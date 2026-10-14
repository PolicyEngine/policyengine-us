from policyengine_us.model_api import *
import numpy as np


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
        cash_50_explicit = add(
            tax_unit, period, ["charitable_cash_donations_50_pct_orgs"]
        )
        cash_to_non_50_pct = add(
            tax_unit, period, ["charitable_cash_donations_non_50_pct_orgs"]
        )
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])

        non_cash_50_explicit = add(
            tax_unit, period, ["charitable_non_cash_donations_50_pct_orgs"]
        )
        non_cash_to_non_50_pct = add(
            tax_unit,
            period,
            ["charitable_non_cash_donations_non_50_pct_orgs"],
        )
        non_cash_donations = add(tax_unit, period, ["charitable_non_cash_donations"])

        cg_to_50_pct = add(
            tax_unit,
            period,
            ["charitable_capital_gain_donations_50_pct_orgs"],
        )
        cg_to_non_50_pct = add(
            tax_unit,
            period,
            ["charitable_capital_gain_donations_non_50_pct_orgs"],
        )
        cg_donations = add(
            tax_unit,
            period,
            ["charitable_capital_gain_donations"],
        )

        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity

        # Resolve category contributions: fallback logic ensures no dollars
        # are dropped if a user specifies both a total and a sub-category.
        cash_50 = where(
            cash_50_explicit > 0,
            cash_50_explicit,
            max_(0, cash_donations - cash_to_non_50_pct),
        )
        cash_non_50 = where(
            cash_to_non_50_pct > 0,
            cash_to_non_50_pct,
            max_(0, cash_donations - cash_50),
        )

        ordinary_50 = where(
            non_cash_50_explicit > 0,
            non_cash_50_explicit,
            max_(0, non_cash_donations - non_cash_to_non_50_pct),
        )
        ordinary_non_50 = where(
            non_cash_to_non_50_pct > 0,
            non_cash_to_non_50_pct,
            max_(0, non_cash_donations - ordinary_50),
        )

        cg_50 = where(
            cg_to_50_pct > 0,
            cg_to_50_pct,
            max_(0, cg_donations - cg_to_non_50_pct),
        )
        cg_non_50 = where(
            cg_to_non_50_pct > 0,
            cg_to_non_50_pct,
            max_(0, cg_donations - cg_50),
        )

        # Worksheet 2, Step 3:
        agi = positive_agi
        limit_50 = p.ceiling.non_cash * agi
        limit_30_non_50 = p.ceiling.non_cash_to_non_50_pct_org * agi
        limit_30_cg_50 = p.ceiling.capital_gain_to_50_pct_org * agi
        limit_20_cg_non_50 = p.ceiling.capital_gain_to_non_50_pct_org * agi

        # 1. Cash contributions subject to limit based on 60% of AGI (Worksheet 2 lines 12-14, IRC § 170(b)(1)(G))
        cash_ceiling = p.ceiling.all * agi
        deductible_cash_50 = min_(cash_50, cash_ceiling)

        # 2. Noncash ordinary contributions subject to limit based on 50% of AGI (Worksheet 2 lines 15-18, IRC § 170(b)(1)(A))
        room_for_ord_50 = max_(0, limit_50 - deductible_cash_50)
        deductible_ord_50 = min_(ordinary_50, room_for_ord_50)

        # 3. Contributions (other than capital gain property) subject to 30% limit (Worksheet 2 lines 19-25, IRC § 170(b)(1)(B))
        contribs_to_50_orgs = cg_50 + ordinary_50 + cash_50
        room_under_50_for_non_50 = max_(0, limit_50 - contribs_to_50_orgs)
        non_50_ordinary_and_cash = cash_non_50 + ordinary_non_50
        deductible_non_50_ordinary = min_(
            non_50_ordinary_and_cash,
            min_(limit_30_non_50, room_under_50_for_non_50),
        )

        # 4. Contributions of capital gain property to 50% limit orgs subject to 30% limit (Worksheet 2 lines 26-31, IRC § 170(b)(1)(C))
        contribs_ord_and_cash_to_50 = ordinary_50 + cash_50
        room_under_50_for_cg_50 = max_(0, limit_50 - contribs_ord_and_cash_to_50)
        deductible_cg_50 = min_(
            cg_50,
            min_(limit_30_cg_50, room_under_50_for_cg_50),
        )

        # 5. Contributions of capital gain property to non-50% limit orgs subject to 20% limit (Worksheet 2 lines 32-41, IRC § 170(b)(1)(D))
        deductible_so_far = (
            deductible_cash_50
            + deductible_ord_50
            + deductible_non_50_ordinary
            + deductible_cg_50
        )
        room_under_50_overall = max_(0, limit_50 - deductible_so_far)
        room_under_30_after_non_50_ord = max_(
            0, limit_30_non_50 - deductible_non_50_ordinary
        )
        room_under_30_after_cg_50 = max_(0, limit_30_non_50 - deductible_cg_50)
        deductible_cg_non_50 = np.minimum.reduce(
            [
                cg_non_50,
                limit_20_cg_non_50,
                room_under_50_overall,
                room_under_30_after_non_50_ord,
                room_under_30_after_cg_50,
            ]
        )

        # Total deductible contributions before floor (Worksheet 2 line 52):
        total_allowed = (
            deductible_cash_50
            + deductible_ord_50
            + deductible_non_50_ordinary
            + deductible_cg_50
            + deductible_cg_non_50
        )

        # 2026+ floor under IRC § 170(b)(1)(I) (P.L. 119-21):
        # Applies to contributions otherwise allowable (after ceilings).
        if p.floor.applies:
            deduction_floor = p.floor.amount * positive_agi
            return max_(0, total_allowed - deduction_floor)

        return total_allowed
