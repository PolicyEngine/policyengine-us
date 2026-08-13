from policyengine_us.model_api import *


class wa_cascade_care_savings_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Cascade Care Savings"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/board/2025/PY2026-Final-CCS-Policy.pdf#page=8",
    )
    documentation = (
        "A tax unit is eligible for Cascade Care Savings when the program is "
        "in effect, household income (ACA MAGI per 26 U.S.C. 36B(d)(2)) is at "
        "or below 250% of the federal poverty line, and at least one member is "
        "a Cascade Care Savings enrollee (Group 1, eligible for the federal "
        "ACA premium tax credit; or Group 3, undocumented and lacking minimum "
        "essential coverage through Washington Apple Health Expansion or Apple "
        "Health for Kids). Section 4(1)(c) imposes only the 250% FPL upper "
        "bound; it sets no income floor. Washington residency is enforced "
        "by defined_for. Not modeled: the Cascade Care standard-plan enrollment "
        "requirement (otherwise-eligible Marketplace enrollees are treated as "
        "Cascade-enrolled), the filing-behavior exclusions of Section 4(2), "
        "the COFA Islander Premium Assistance ineligibility test, and Group 2."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.wahbe.cascade_care_savings
        in_effect = p.in_effect
        magi_fraction = tax_unit("aca_magi_fraction", period)
        income_eligible = magi_fraction <= p.fpl_limit
        has_eligible_member = (
            add(tax_unit, period, ["wa_cascade_care_savings_member_eligible"]) > 0
        )
        return in_effect & income_eligible & has_eligible_member
