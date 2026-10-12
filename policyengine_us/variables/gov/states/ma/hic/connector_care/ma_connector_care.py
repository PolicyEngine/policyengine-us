from policyengine_us.model_api import *


class ma_connector_care(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts ConnectorCare"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MA
    reference = (
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=5",
        "https://www.mahealthconnector.org/wp-content/uploads/amended-956CMR12.00.pdf#page=6",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=1",
        "https://www.mahealthconnector.org/wp-content/uploads/ConnectorCare-Overview-2026.pdf#page=2",
    )
    documentation = (
        "Massachusetts ConnectorCare, the Health Connector's state premium "
        "wrap on top of the federal ACA premium tax credit. The state pays "
        "carriers the residual between the benchmark plan premium, the federal "
        "APTC, and a flat monthly per-person enrollee premium set annually by "
        "the Board per Plan Type (956 CMR 12.12(9)). Since PY2025 the enrollee "
        "contribution is a flat dollar amount per FPL band, decoupled from the "
        "affordability percent-of-income schedule. The household enrollee "
        "contribution is the per-person monthly premium times the number of "
        "APTC-eligible members times MONTHS_IN_YEAR (per-person aggregation, "
        "CO/WA convention), assuming full-year enrollment. "
        "Approximations: SLCSP (the ACA benchmark, second-lowest-cost silver) "
        "proxies the lowest-cost ConnectorCare-designated plan the state "
        "guarantee actually references, which slightly overstates the wrap "
        "where the lowest-cost ConnectorCare plan is below SLCSP; the full "
        "federal APTC is netted because 956 CMR 12.04(3)(c) conditions the "
        "minimum premium on the enrollee electing the full amount of APTC "
        "available; and the subsidy is floored at zero, since high-FPL bands "
        "can have APTC plus the enrollee contribution exceeding SLCSP (no "
        "clawback). The cost-sharing wrap (reduced co-pays and out-of-pocket "
        "maximums) is a separate benefit and is not modeled. ConnectorCare is "
        "paid to carriers rather than as a tax credit, so it is not routed "
        "through taxable income and no reconciliation is modeled. The amended "
        "956 CMR still carries un-repealed 500% FPL and Plan Type 3D pilot "
        "text, but the operational 2026 Overview runs 100-400% FPL only; a "
        "future re-expansion is a parameter change."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.hic.connector_care
        n_members = add(tax_unit, period, ["ma_connector_care_member_eligible"])
        magi_fraction = tax_unit("aca_magi_fraction", period)
        per_person_monthly = p.enrollee_premium.calc(magi_fraction)
        enrollee_contribution = MONTHS_IN_YEAR * per_person_monthly * n_members
        # SLCSP is a MONTH variable summed to the year to proxy the benchmark
        # ConnectorCare plan; the full APTC is netted per 956 CMR 12.04(3)(c).
        slcsp_annual = add(tax_unit, period, ["slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        subsidy = max_(0, slcsp_annual - aca_ptc - enrollee_contribution)
        eligible = tax_unit("ma_connector_care_eligible", period)
        return where(eligible, subsidy, 0)
