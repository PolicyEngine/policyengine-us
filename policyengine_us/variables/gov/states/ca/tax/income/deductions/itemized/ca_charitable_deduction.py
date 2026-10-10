from policyengine_us.model_api import *


class ca_charitable_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California charitable contribution deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA
    reference = (
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17024.5",
        "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17250.1",
        "https://www.ftb.ca.gov/forms/2025/2025-540-ca-instructions.html",
    )

    def formula(tax_unit, period, parameters):
        cash = add(tax_unit, period, ["charitable_cash_donations"])
        non_cash = add(tax_unit, period, ["charitable_non_cash_donations"])
        non_cash_non_50 = add(
            tax_unit, period, ["charitable_non_cash_donations_non_50_pct_orgs"]
        )
        non_cash_50 = non_cash - non_cash_non_50
        agi = tax_unit("positive_agi", period)
        p = parameters(period).gov.states.ca.tax.income.deductions.itemized.charity

        # Retain the existing donation categories: the 50% category models
        # the basis-reduction election for capital-gain property. The default
        # 30% capital-gain-property cap, 20% private-foundation category, cash
        # split by organization, and carryovers need more granular inputs.
        capped_non_cash = min_(non_cash_50, p.ceiling.non_cash * agi) + min_(
            non_cash_non_50, p.ceiling.non_cash_to_non_50_pct_org * agi
        )
        # Schedule CA Part II lines 11-12: California retains the 50% ceiling
        # and does not adopt the post-conformity-date federal charitable floor.
        return min_(cash + capped_non_cash, p.ceiling.all * agi)
