from policyengine_us.model_api import *


class nj_njhps(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Health Plan Savings"
    unit = USD
    definition_period = YEAR
    defined_for = "nj_njhps_eligible"
    reference = (
        "https://www.cms.gov/files/document/1332-ota-methodology-addendum-nj-pass-through.pdf#page=8",
        "https://pub.njleg.gov/bills/2020/AL20/61_.HTM",
    )
    documentation = (
        "New Jersey Health Plan Savings, the state premium subsidy "
        "administered by Get Covered NJ under the Department of Banking and "
        "Insurance, established by P.L. 2020 c.61. The state pays carriers a "
        "flat per-member-per-month (PMPM) amount set by FPL band, ADDED on top "
        "of the federal Advance Premium Tax Credit (APTC) rather than netted "
        "against an enrollee contribution. The household base amount is the "
        "band PMPM times the number of eligible members times MONTHS_IN_YEAR. "
        "Because the combined subsidy cannot lower the net premium below zero, "
        "the amount is capped at the premium remaining after APTC "
        "(max(0, SLCSP - APTC)); there is no clawback. "
        "Approximations: SLCSP (the ACA benchmark, second-lowest-cost silver) "
        "proxies the enrolled/benchmark plan premium, which slightly "
        "overstates the cap where the enrolled plan is cheaper than SLCSP "
        "(same approximation Washington and Massachusetts document). In the "
        "400-600% FPL band the federal APTC is $0 (the 400% FPL cliff reverts "
        "for PY2026), so the post-APTC residual equals the full SLCSP annual "
        "premium and NJHPS is the sole premium subsidy there; this also "
        "requires the non-income eligibility gating in "
        "nj_njhps_member_eligible, since is_aca_ptc_eligible is False above "
        "400% FPL. Full-year enrollment is assumed via the MONTHS_IN_YEAR "
        "annualization (partial-year enrollment is not modeled). NJHPS is paid "
        "to carriers rather than as a tax credit, so it is not routed through "
        "taxable income and no reconciliation or tax-return interaction is "
        "modeled."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nj.dobi.njhps
        n_members = add(tax_unit, period, ["nj_njhps_member_eligible"])
        magi_fraction = tax_unit("aca_magi_fraction", period)
        per_member_monthly = p.pmpm.calc(magi_fraction)
        base_annual = MONTHS_IN_YEAR * per_member_monthly * n_members
        # SLCSP is a MONTH variable summed to the year to proxy the benchmark
        # plan premium. NJHPS is added atop APTC and cannot lower the net
        # premium below zero, so it is capped at the post-APTC residual. In the
        # 400-600% band aca_ptc is 0, so the residual equals slcsp_annual.
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        residual = max_(0, slcsp_annual - aca_ptc)
        return min_(base_annual, residual)
