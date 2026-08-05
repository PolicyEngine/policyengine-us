from policyengine_us.model_api import *


class nm_premium_assistance(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico Premium Assistance"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = (
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=5",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/15a6c1dd-e12b-4ffb-95af-bb54262218f3/FINAL-PY26%20%20MAP%20Policy%20and%20Procedures%20Manual.pdf#page=6",
        "https://api.realfile.rtsclients.com/PublicFiles/6c91aefc960e463485b3474662fd7fd2/50c9a4d0-d5c8-48aa-8b9a-5c43e8fa23bc/Addendum%201_MAP%20P&P%20Middle%20Income%20Household.pdf#page=3",
    )
    documentation = (
        "New Mexico state top-up to the federal ACA premium tax credit. Base "
        "assistance (household income at or below 400% FPL) reduces the "
        "enrollee's required contribution toward the benchmark SLCSP from the "
        "federal residual to the lower New Mexico target percentage; for "
        "enrollees at or below 200% FPL the benchmark is grossed up by 10%. "
        "The Middle Income Household component (income above 400% FPL) caps "
        "the benchmark SLCSP at 8.5% of household income. Both amounts are "
        "floored at zero; the selected-plan cap is approximated by the "
        "SLCSP-based residual."
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

        # Base NMPA: gross up the benchmark by 10% at or below the gross-up FPL
        # limit, subtract the federal APTC and the target contribution, floor
        # at zero.
        gross_up = where(
            magi_frac <= p.benchmark_gross_up.fpl_limit,
            1 + p.benchmark_gross_up.rate,
            1,
        )
        benchmark = slcsp * gross_up
        target_percentage = tax_unit(
            "nm_premium_assistance_target_contribution_percentage", period
        )
        base_amount = max_(0, benchmark - aca_ptc - target_percentage * income)

        # Middle Income Household: cap the plain benchmark SLCSP at the MIH
        # rate of household income. aca_ptc is zero above 400% FPL in the 2026
        # baseline but is subtracted for robustness to reform scenarios.
        mih_amount = max_(0, slcsp - aca_ptc - p.mih.rate * income)

        base_eligible = tax_unit("nm_premium_assistance_eligible", period)
        mih_eligible = tax_unit("nm_mih_eligible", period)
        return select(
            [base_eligible, mih_eligible],
            [base_amount, mih_amount],
            default=0,
        )
