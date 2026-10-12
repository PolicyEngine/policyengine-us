from policyengine_us.model_api import *


class md_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maryland Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = "md_premium_assistance_eligible"
    # COMAR 14.35.21 (codified chapter, permanent effective 2025-10-13). The
    # basis-of-calculation rule .04B-C and the Board delegation .04D are on
    # page 6 of the codified chapter. The emergency PDF (25-134E) expired
    # 2026-01-06.
    reference = (
        "https://regs.maryland.gov/us/md/exec/comar/14.35.21#page=6",
        "https://mgaleg.maryland.gov/meeting_material/2025/hgo%20-%20134051066649659653%20-%20Combined%20MHBE.MIA%20slides_10.16.2025%20briefing%20to%20HGO&Finance.pdf#page=58",
    )
    # Maryland state top-up to the federal ACA premium tax credit. Per COMAR
    # 14.35.21.04B, the subsidy equals the benchmark SLCSP premium remaining
    # after the federal APTC, less the enrollee's Maryland target
    # contribution (the target percentage applied to income). This "premium
    # balance after APTC" form never duplicates the federal credit.
    #
    # For enrollees with a 0% target contribution the program also covers the
    # non-essential-health-benefit premium components so their net premium is
    # $0, but this non-EHB split is not modeled here.
    #
    # A non-filer has aca_ptc = 0, which would inflate the post-APTC premium
    # balance and over-grant the state subsidy. COMAR 14.35.21.03A(1)
    # conditions the subsidy on APTC eligibility, which requires filing, so
    # the subsidy is gated on tax_unit_is_filer below.
    #
    # The display name "Premium Assistance" follows the MHBE consumer-facing
    # site ("Maryland Premium Assistance"); the statute and COMAR title the
    # program the "State-Based Health Insurance Subsidies Program".
    #
    # Not modeled: the April 1, 2026 enrollment cutoff and .03C budget-cap
    # authority, the mid-2026 special-enrollment-period closure, the Board's
    # budget-limit authority, the requirement to enroll in a QHP through the
    # Exchange (.02B(1)), and the monthly eligibility timing in .03E (this
    # variable uses a year period).

    def formula(tax_unit, period, parameters):
        income = max_(tax_unit("aca_magi", period), 0)
        md_percentage = tax_unit(
            "md_premium_assistance_target_contribution_percentage", period
        )
        # slcsp is a MONTH-period variable; core sums the 12 months when
        # called from this YEAR formula.
        slcsp = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        # Premium balance remaining after the federal APTC (COMAR .04B).
        premium_after_aptc = max_(0, slcsp - aca_ptc)
        subsidy = max_(0, premium_after_aptc - md_percentage * income)
        # Gate on filing: non-filers are not APTC-eligible (COMAR .03A(1)).
        is_filer = tax_unit("tax_unit_is_filer", period)
        return where(is_filer, subsidy, 0)
