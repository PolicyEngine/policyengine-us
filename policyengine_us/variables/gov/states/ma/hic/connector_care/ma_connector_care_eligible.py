from policyengine_us.model_api import *


class ma_connector_care_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Massachusetts ConnectorCare"
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        # 956 CMR 12.03 defines Household, Federal Poverty Level and MAGI.
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=4",
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=5",
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=6",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=1",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=2",
        # The Health Connector uses the 2025 guidelines for plan year 2026 and
        # the 2026 guidelines for plan year 2027.
        "https://www.mahealthconnector.org/wp-content/uploads/ConsumerGuideToSubsidies-2026.pdf#page=1",
        "https://www.mahealthconnector.org/wp-content/uploads/Health-Connector-Guide-to-Subsidies-2027-ENG.pdf#page=1",
    )
    documentation = (
        "A tax unit is eligible for ConnectorCare when the program is in "
        "effect, household income (ACA MAGI per 26 U.S.C. 36B(d)(2)) as a "
        "share of aca_fpg (the prior-year federal poverty guideline for the "
        "section 36B tax family), measured as the exact ratio rather than the "
        "truncated aca_magi_fraction, is at or "
        "above the 100% FPL floor and at or below the FPL limit (400% for "
        "PY2026 and PY2027 under the ConnectorCare Expansion Pilot, St. 2023 "
        "c.28 s.81 as extended by St. 2026 c.137 s.92; 300% from PY2028, the "
        "limit in M.G.L. c.176Q s.3(b)), and "
        "at least one member is eligible for the federal ACA premium tax "
        "credit. Massachusetts residency is enforced by defined_for. The "
        "amended 956 CMR still defines a sub-100% Plan Type 1 and a 400.1-500% "
        "Plan Type 3D, but the 2026 ConnectorCare Overview and the 2027 Guide "
        "to Subsidies run Plan Types 2A-3C only (100-400% FPL), and that "
        "operational reading is treated as controlling."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.hic.connector_care
        in_effect = p.in_effect
        # 956 CMR 12.04(3)(b) bounds Plan Type 3C by income "not over 400% of
        # the FPL". Test the exact ratio, not the truncated aca_magi_fraction:
        # truncation maps 400.00%-400.99% to 4.00, which would admit incomes
        # above 400%. The floor ("at least 100%") is unaffected by truncation.
        # 956 CMR 12.03 sets the guideline year, which aca_fpg matches: the FPL
        # is the guideline most recently published as of the first day of open
        # enrollment. Its Household is the tax filer and the people the filer
        # expects to claim, like the section 36B tax family, but it doesn't
        # say whether a filer who can be claimed on another return counts.
        # Leaving that filer out, as aca_fpg does, is a modeling choice.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = (exact_magi_frac >= p.fpl_floor) & (
            exact_magi_frac <= p.fpl_limit
        )
        has_eligible_member = (
            add(tax_unit, period, ["ma_connector_care_member_eligible"]) > 0
        )
        return in_effect & income_eligible & has_eligible_member
