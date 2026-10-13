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
        # 26 USC 170(b)(1) defines contribution categories with separate AGI caps:
        #   (G) Cash to 50% limit orgs: 60% AGI (post-TCJA; 50% pre-2018; 100% 2020-2021)
        #   (A) Non-cash ordinary / non-capital-gain to 50% limit orgs: 50% AGI
        #   (C) Capital gain property to 50% limit orgs: 30% AGI (or 50% with basis reduction)
        #   (B) Cash & non-cash ordinary to non-50% limit orgs: 30% AGI
        #   (D) Capital gain property to non-50% limit orgs: 20% AGI
        cash_donations = add(tax_unit, period, ["charitable_cash_donations"])
        cash_to_non_50_pct = add(
            tax_unit, period, ["charitable_cash_donations_non_50_pct_orgs"]
        )
        non_cash_donations = add(tax_unit, period, ["charitable_non_cash_donations"])
        non_cash_to_non_50_pct = add(
            tax_unit,
            period,
            ["charitable_non_cash_donations_non_50_pct_orgs"],
        )
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

        positive_agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.irs.deductions.itemized.charity

        # Resolve category amounts
        cash_non_50 = cash_to_non_50_pct
        cash_50 = max_(0, cash_donations - cash_to_non_50_pct)

        cg_50 = cg_to_50_pct
        cg_non_50 = cg_to_non_50_pct

        ordinary_non_50 = non_cash_to_non_50_pct
        ordinary_50 = max_(0, non_cash_donations - non_cash_to_non_50_pct)

        if p.floor.applies:
            deduction_floor = p.floor.amount * positive_agi

            reduced_ordinary_50 = max_(ordinary_50 - deduction_floor, 0)
            floor_rem = max_(deduction_floor - ordinary_50, 0)

            reduced_cg_50 = max_(cg_50 - floor_rem, 0)
            floor_rem = max_(floor_rem - cg_50, 0)

            reduced_ordinary_non_50 = max_(ordinary_non_50 - floor_rem, 0)
            floor_rem = max_(floor_rem - ordinary_non_50, 0)

            reduced_cg_non_50 = max_(cg_non_50 - floor_rem, 0)
            floor_rem = max_(floor_rem - cg_non_50, 0)

            reduced_cash_50 = max_(cash_50 - floor_rem, 0)
            floor_rem = max_(floor_rem - cash_50, 0)

            reduced_cash_non_50 = max_(cash_non_50 - floor_rem, 0)

            ordinary_50 = reduced_ordinary_50
            cg_50 = reduced_cg_50
            ordinary_non_50 = reduced_ordinary_non_50
            cg_non_50 = reduced_cg_non_50
            cash_50 = reduced_cash_50
            cash_non_50 = reduced_cash_non_50

        # Statutory caps per 26 USC 170(b)(1):
        # 1. 50% limit orgs:
        #    - Non-cash ordinary capped at 50% of AGI (170(b)(1)(A))
        #    - Capital gain property capped at 30% of AGI (170(b)(1)(C)(i))
        #    - Total non-cash to 50% orgs capped at 50% of AGI
        capped_ordinary_50 = min_(ordinary_50, p.ceiling.non_cash * positive_agi)
        capped_cg_50 = min_(cg_50, p.ceiling.capital_gain_to_50_pct_org * positive_agi)
        capped_non_cash_50 = min_(
            capped_ordinary_50 + capped_cg_50,
            p.ceiling.non_cash * positive_agi,
        )

        # 2. Non-50% limit orgs:
        #    - Capital gain property capped at 20% of AGI (170(b)(1)(D))
        #    - Total contributions to non-50% orgs capped at 30% of AGI (170(b)(1)(B))
        capped_cg_non_50 = min_(
            cg_non_50,
            p.ceiling.capital_gain_to_non_50_pct_org * positive_agi,
        )
        capped_non_50 = min_(
            cash_non_50 + ordinary_non_50 + capped_cg_non_50,
            p.ceiling.cash_to_non_50_pct_org * positive_agi,
        )

        # 3. Overall deduction capped at overall ceiling (60% post-TCJA per 170(b)(1)(G))
        total_cap = p.ceiling.all * positive_agi
        return round_(
            min_(
                capped_non_cash_50 + capped_non_50 + cash_50,
                total_cap,
            ),
            2,
        )
