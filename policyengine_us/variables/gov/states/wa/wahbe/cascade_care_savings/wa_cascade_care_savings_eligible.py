from policyengine_us.model_api import *


class wa_cascade_care_savings_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Washington Cascade Care Savings"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/rcw/default.aspx?cite=43.71.110",
        "https://www.wahbexchange.org/content/dam/wahbe-assets/materials/collateral/cc/FinalPY2026CascadeCareSavingsPolicy_Combined.pdf#page=11",
        # Final PY2027 policy, Section 3(9): the Federal Poverty Level is the
        # measure specified in 26 U.S.C. 36B(d)(3)(B).
        "https://www.wahbexchange.org/content/dam/materials/communications/policy/2026/Final_PY_2027_Cascade_Care_Savings_Policy.pdf#page=2",
    )
    documentation = (
        "A tax unit is eligible for Cascade Care Savings when the program is "
        "in effect, household income (ACA MAGI per 26 U.S.C. 36B(d)(2)) is at "
        "or below 250% of the federal poverty line for the premium tax credit "
        "tax family (aca_fpg, the prior-year guideline), measured as the exact "
        "ratio rather than the truncated aca_magi_fraction, and at "
        "least one member is "
        "a Cascade Care Savings enrollee (Group 1, eligible for the federal "
        "ACA premium tax credit; Group 2, enrolled outside the federal tax "
        "family; or Group 3, undocumented and lacking minimum "
        "essential coverage through Washington Apple Health Expansion or Apple "
        "Health for Kids). Section 4(1)(c) imposes only the 250% FPL upper "
        "bound; it sets no income floor. Washington residency is enforced "
        "by defined_for. Not modeled: the Cascade Care standard-plan enrollment "
        "requirement (otherwise-eligible Marketplace enrollees are treated as "
        "Cascade-enrolled), the filing-behavior exclusions of Section 4(2), "
        "the COFA Islander Premium Assistance ineligibility test, and other "
        "Group 2 members not identifiable in the model."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wa.wahbe.cascade_care_savings
        in_effect = p.in_effect
        # Section 4(1)(c) covers income "up to 250% of the Federal Poverty
        # Level". Test the exact ratio, not the truncated aca_magi_fraction:
        # truncation maps 250.00%-250.99% to 2.50, which would admit incomes
        # above 250%. Section 3(9) defines that level by 26 U.S.C.
        # 36B(d)(3)(B), so the poverty line is aca_fpg, the same line that
        # aca_magi_fraction and the federal credit divide by.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = exact_magi_frac <= p.fpl_limit
        has_eligible_member = (
            add(tax_unit, period, ["wa_cascade_care_savings_member_eligible"]) > 0
        )
        return in_effect & income_eligible & has_eligible_member
