from policyengine_us.model_api import *


class ma_connector_care(Variable):
    value_type = float
    entity = TaxUnit
    label = "Massachusetts ConnectorCare"
    unit = USD
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
        "future re-expansion is a parameter change. Plan Type 3C (300-400% "
        "FPL) exists only under the ConnectorCare Expansion Pilot, which ends "
        "after PY2027, so from PY2028 the income limit is 300% FPL."
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ma.hic.connector_care
        n_members = add(tax_unit, period, ["ma_connector_care_member_eligible"])
        # 956 CMR 12.04(3)(b) assigns Plan Types by exact income bands that
        # include their upper edge: "at or below 150%" is 2A, "over 150% and
        # not over 200%" is 2B, and so on. Look up the exact ratio, not the
        # truncated aca_magi_fraction (which put 150.00%-150.99% in 2A), with
        # each bracket closed on the right. ma_connector_care_eligible explains
        # the choice of aca_fpg as the poverty line.
        magi = max_(tax_unit("aca_magi", period), 0)
        fpg = tax_unit("aca_fpg", period)
        # Divide in float64: a float32 quotient can round a ratio just above
        # a limit down onto it.
        exact_magi_frac = magi.astype(np.float64) / fpg
        per_person_monthly = p.enrollee_premium.calc(exact_magi_frac, right=True)
        enrollee_contribution = MONTHS_IN_YEAR * per_person_monthly * n_members
        # The benchmark for the federal coverage family (a MONTH variable
        # summed to the year) proxies the benchmark ConnectorCare plan of the
        # APTC-eligible enrollees (956 CMR 12.04(3)(a)2); the full APTC is
        # netted per 956 CMR 12.04(3)(c).
        slcsp_annual = add(tax_unit, period, ["aca_ptc_slcsp"])
        aca_ptc = tax_unit("aca_ptc", period)
        subsidy = max_(0, slcsp_annual - aca_ptc - enrollee_contribution)
        eligible = tax_unit("ma_connector_care_eligible", period)
        return where(eligible, subsidy, 0)
