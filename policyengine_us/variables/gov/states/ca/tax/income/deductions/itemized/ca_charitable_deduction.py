from policyengine_us.model_api import *
from policyengine_us.variables.gov.irs.income.taxable_income.deductions.itemizing.charitable_deduction import (
    compute_charitable_deduction,
)


class ca_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California charitable contribution deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17024.5",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17201",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17250.1",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )

    def formula(tax_unit, period, parameters):
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
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.charity

        # Schedule CA Part II lines 11-12 and R&TC §§ 17024.5, 17201, 17250.1:
        # California conforms to the pre-TCJA IRC § 170(b) 5-tier limits (50% overall/cash/ordinary,
        # 30% non-50% orgs, 30% capital gains to 50% orgs, 20% capital gains to non-50% orgs),
        # without adopting the TCJA 60% cash limit, CARES Act 100% qualified cash election,
        # 2026+ 10% non-50% cash add-back, or the federal charitable deduction floor.
        return compute_charitable_deduction(
            cash_50=cash_50,
            cash_non_50=cash_non_50,
            ordinary_50=ordinary_50,
            ordinary_non_50=ordinary_non_50,
            cg_50=cg_50,
            cg_non_50=cg_non_50,
            positive_agi=positive_agi,
            ceiling_all=p.ceiling.non_cash,
            ceiling_non_cash=p.ceiling.non_cash,
            ceiling_non_50=p.ceiling.non_cash_to_non_50_pct_org,
            ceiling_cg_50=p.ceiling.capital_gain_to_50_pct_org,
            ceiling_cg_non_50=p.ceiling.capital_gain_to_non_50_pct_org,
            non_50_pct_cash_add_back=0.0,
            qualified_cash_election=False,
        )
