from policyengine_us.model_api import *


class charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Charitable deduction"
    unit = USD
    documentation = "Deduction from taxable income for charitable donations."
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/170"

    def formula(tax_unit, period, parameters):
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash_donations = add(
            tax_unit, period, ["charitable_non_cash_donations"]
        )
        non_cash_to_non_50_pct = add(
            tax_unit,
            period,
            ["charitable_non_cash_donations_to_non_50_percent_limit_orgs"],
        )
        non_cash_to_50_pct = non_cash_donations - non_cash_to_non_50_pct
        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity

        # Cap non-cash to 50% limit orgs at 50% of AGI per
        # 26 USC 170(b)(1)(A).
        capped_non_cash_50 = min_(
            non_cash_to_50_pct, p.ceiling.non_cash * positive_agi
        )
        # Cap non-cash to non-50% limit orgs at 30% of AGI per
        # 26 USC 170(b)(1)(B).
        capped_non_cash_30 = min_(
            non_cash_to_non_50_pct,
            p.ceiling.non_cash_to_non_50_pct_org * positive_agi,
        )
        capped_non_cash = capped_non_cash_50 + capped_non_cash_30

        total_cap = p.ceiling.all * positive_agi
        if p.floor.applies:
            deduction_floor = p.floor.amount * positive_agi
            reduced_non_cash_50 = max_(non_cash_to_50_pct - deduction_floor, 0)
            capped_reduced_non_cash_50 = min_(
                reduced_non_cash_50, p.ceiling.non_cash * positive_agi
            )

            remaining_floor_after_50 = max_(
                deduction_floor - non_cash_to_50_pct, 0
            )
            reduced_non_cash_30 = max_(
                non_cash_to_non_50_pct - remaining_floor_after_50, 0
            )
            capped_reduced_non_cash_30 = min_(
                reduced_non_cash_30,
                p.ceiling.non_cash_to_non_50_pct_org * positive_agi,
            )

            remaining_floor = max_(
                remaining_floor_after_50 - non_cash_to_non_50_pct, 0
            )
            reduced_cash_donations = max_(cash_donations - remaining_floor, 0)
            return min_(
                capped_reduced_non_cash_50
                + capped_reduced_non_cash_30
                + reduced_cash_donations,
                total_cap,
            )
        return min_(capped_non_cash + cash_donations, total_cap)
