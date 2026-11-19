from policyengine_us.model_api import *


class md_premium_assistance_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for Maryland Premium Assistance"
    definition_period = YEAR
    defined_for = StateCode.MD
    # COMAR 14.35.21.03 (eligibility) is on page 5 of the codified chapter,
    # permanent effective 2025-10-13. The emergency PDF (25-134E) expired
    # 2026-01-06. HGO briefing p.58 documents the all-ages eligibility design.
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/14.35.21#page=5",
        "https://mgaleg.maryland.gov/meeting_material/2025/hgo%20-%20134051066649659653%20-%20Combined%20MHBE.MIA%20slides_10.16.2025%20briefing%20to%20HGO&Finance.pdf#page=58",
        # COMAR 14.35.21.02B(3): the federal poverty level is the guidelines
        # most recently published as of the first day of open enrollment.
        "https://regs.maryland.gov/us/md/exec/comar/14.35.21.02#B(3)",
        # MHBE adopted PY2026 and published PY2027 subsidy parameters.
        "https://www.marylandhbe.com/wp-content/uploads/2025/08/2026-State-Subsidy-and-Reinsurance-Parameters-8-18-25.pdf#page=30",
        "https://www.marylandhbe.com/wp-content/uploads/2026/08/2027-Final-State-Subsidy-and-Estimated-Reinsurance-Parameters.pdf#page=25",
        # MHBE's income thresholds use the 2025 guidelines for PY2026 and the
        # 2026 guidelines for PY2027.
        "https://www.marylandhbe.com/wp-content/uploads/2025/08/2026-State-Subsidy-and-Reinsurance-Parameters-8-18-25.pdf#page=16",
        "https://www.marylandhbe.com/wp-content/uploads/2026/08/2027-Final-State-Subsidy-and-Estimated-Reinsurance-Parameters.pdf#page=12",
    )
    # A tax unit is eligible for Maryland Premium Assistance when the program
    # is in effect, at least one member is eligible for the federal ACA
    # premium tax credit, and household income is at or below the federal
    # poverty line limit, on the exact ratio of ACA MAGI to aca_fpg (the
    # prior-year guideline for the section 36B tax family).

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.md.mhbe.premium_assistance
        in_effect = p.in_effect
        # At least one member must be eligible for the federal ACA PTC.
        aptc_eligible = add(tax_unit, period, ["is_aca_ptc_eligible"]) > 0
        # The MHBE design sets "No state subsidy above 400% FPL" (PY2026) and
        # "Eligibility: 400% FPL or below" (PY2027). Test the exact ratio, not
        # the truncated aca_magi_fraction: truncation maps 400.00%-400.99% to
        # 4.00, which would admit incomes above 400%. COMAR 14.35.21.02B(3)
        # and the MHBE thresholds set the guideline year, which aca_fpg
        # matches. Neither defines the family size counted, so using the
        # section 36B tax family is a modeling choice: aca_fpg is the line of
        # the federal credit this gate already requires.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        income_eligible = exact_magi_frac <= p.fpl_limit
        return in_effect & aptc_eligible & income_eligible
