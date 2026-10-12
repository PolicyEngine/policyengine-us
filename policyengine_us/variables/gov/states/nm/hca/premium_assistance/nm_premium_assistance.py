from policyengine_us.model_api import *


class nm_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    # New Mexico state top-up to the federal ACA premium tax credit. Base
    # assistance (income up to 400% FPL) reduces the enrollee's required
    # contribution toward the benchmark SLCSP from the federal residual to the
    # lower New Mexico target percentage; up to 200% FPL the benchmark is
    # grossed up by 10%. The Middle Income Household component (income above
    # 400% FPL) caps the benchmark SLCSP at 8.5% of household income.
    #
    # KNOWN BIAS (one-sided, non-negative): the manual caps New Mexico
    # Premium Assistance at the enrollee's SELECTED plan premium, but
    # PolicyEngine has no plan-selection input, so the selected-plan $0 cap is
    # unimplemented and the amount is approximated by the SLCSP-based residual.
    # Up to 200% FPL (target 0%, gross-up on) even a benchmark purchaser is
    # over-credited by up to 10% of the annual SLCSP; the modeled New Mexico
    # Premium Assistance and state cost are therefore biased HIGH, never low.
    # This is repair option (b): document the bias rather than cap the amount.
    # Option (a) - capping the amount at the SLCSP - was declined because it
    # would neutralize the gross-up. Reviewers may request option (a) instead.
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=5",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=6",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/50c9a4d0-d5c8-48aa-8b9a-5c43e8fa23bc/Addendum%201_MAP%20P&P%20Middle%20Income%20Household.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.hca.premium_assistance
        # Clamp income to zero so a negative ACA MAGI cannot inflate the top-up
        # above the benchmark - APTC residual via the -pct*income term.
        income = max_(tax_unit("aca_magi", period), 0)
        # slcsp is a MONTH-period variable; core sums the 12 months when
        # called from this YEAR formula.
        slcsp = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        magi_frac = tax_unit("aca_magi_fraction", period)

        # Base NMPA: gross up the benchmark by 10% up to the gross-up FPL limit,
        # subtract the federal APTC and the target contribution, floor at zero.
        # PY2026 treats the 200% FPL limit as inclusive; PY2027 treats it as
        # strict (below 200% FPL), toggled by benchmark_gross_up.boundary_inclusive.
        limit = p.benchmark_gross_up.fpl_limit
        gross_up_applies = where(
            p.benchmark_gross_up.boundary_inclusive,
            magi_frac <= limit,
            magi_frac < limit,
        )
        gross_up = where(gross_up_applies, 1 + p.benchmark_gross_up.rate, 1)
        benchmark = slcsp * gross_up
        target_percentage = tax_unit(
            "nm_premium_assistance_target_contribution_percentage", period
        )
        base_amount = max_(0, benchmark - aca_ptc - target_percentage * income)

        # Middle Income Household: cap the plain benchmark SLCSP at the MIH rate
        # of household income. The printed MAP Addendum formula is
        # SLCSP - (Applicable% * Income) with no APTC term. NOTE: subtracting
        # aca_ptc matches 8.401.2.8(D)(1)(a) NMAC (state subsidy nets out any
        # federal APTC) and is inert in the PY2026 baseline where APTC is $0
        # above 400% FPL; it only diverges under a reform that restores APTC there.
        mih_amount = max_(0, slcsp - aca_ptc - p.mih.rate * income)

        base_eligible = tax_unit("nm_premium_assistance_eligible", period)
        mih_eligible = tax_unit("nm_premium_assistance_mih_eligible", period)
        return select(
            [base_eligible, mih_eligible],
            [base_amount, mih_amount],
            default=0,
        )
