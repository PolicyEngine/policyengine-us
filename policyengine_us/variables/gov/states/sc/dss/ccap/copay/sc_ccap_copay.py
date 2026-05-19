from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sc_ccap_copay(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "South Carolina CCAP monthly family copay"
    definition_period = MONTH
    defined_for = StateCode.SC
    reference = (
        "https://www.scchildcare.org/media/ubhdm1at/1-13-2025_policy-manual.pdf#page=86",
        "https://www.scchildcare.org/media/n3qmcb5u/sc-child-care-scholarship-program-fee-scale-2023-2024.pdf#page=1",
        "https://www.scchildcare.org/media/ih2mrjw5/fee-scale-2025-2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sc.dss.ccap.copay
        monthly_income = spm_unit("sc_ccap_countable_income", period)
        tier_count = len(p.smi_tier_ratios.thresholds)

        size = spm_unit("spm_unit_size", period.this_year)
        max_size = int(p.max_family_size)
        fee_scale_size = min_(size, max_size)

        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)

        # Family-level copay exemptions (Section 3.4.2, p.108).
        # Head Start copay waiver is per-child, handled below.
        protective = spm_unit("sc_ccap_protective_services", period)
        is_tanf = spm_unit("is_tanf_enrolled", period)
        p_elig = parameters(period).gov.states.sc.dss.ccap.eligibility
        person = spm_unit.members
        is_disabled = person("is_disabled", period.this_year)
        is_young = person("age", period.this_year) < p_elig.disabled_child_age_limit
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        has_disabled_child = spm_unit.any(is_disabled & is_young & is_dependent)

        # Compute copay tier from income position in the fee scale.
        # Pre-2024-10-01: tiers at fixed SMI ratios (45/55/65/75% mark
        #   boundaries between 5 tiers).
        # Post-2024-10-01: equal-width bands from 150% FPL to 85% SMI.
        tier = np.zeros_like(monthly_income, dtype=int)
        below_fpl_threshold = np.zeros_like(monthly_income, dtype=bool)
        zero_only_row = np.zeros_like(monthly_income, dtype=bool)
        if p.fpg_exempt_in_effect:
            max_paid_size = int(p.max_paid_family_size)
            zero_only_row = fee_scale_size > max_paid_size

            # Rows 15-16 are $0-only on the published fee scale. For rows with
            # paid tiers, fall back to the largest published paid-tier size
            # whose derived 150% FPL and 85% SMI bounds still form a
            # nonnegative band.
            paid_band_size = np.ones_like(size, dtype=int)
            for candidate in range(1, max_paid_size + 1):
                lower_candidate = np.floor(
                    fpg(candidate, state_group, period, parameters)
                    / MONTHS_IN_YEAR
                    * p.fpg_exempt_rate
                    + 0.5
                )
                upper_candidate = np.floor(
                    smi(candidate, state, period, parameters)
                    / MONTHS_IN_YEAR
                    * p.smi_tier_ratios.calc(tier_count)
                    + 0.5
                )
                valid_candidate = (fee_scale_size >= candidate) & (
                    lower_candidate <= upper_candidate
                )
                paid_band_size = where(
                    valid_candidate,
                    candidate,
                    paid_band_size,
                )

            monthly_fpg = (
                fpg(paid_band_size, state_group, period, parameters) / MONTHS_IN_YEAR
            )
            monthly_smi = (
                smi(paid_band_size, state, period, parameters) / MONTHS_IN_YEAR
            )
            lower = np.floor(monthly_fpg * p.fpg_exempt_rate + 0.5)
            upper = np.floor(monthly_smi * p.smi_tier_ratios.calc(tier_count) + 0.5)
            band_width = np.ceil((upper - lower) / tier_count)
            below_fpl_threshold = (~zero_only_row) & (monthly_income <= lower)
            for i in range(1, tier_count):
                threshold = lower + band_width * i
                tier = tier + ((~zero_only_row) & (monthly_income > threshold)).astype(
                    int
                )
        else:
            monthly_smi = (
                smi(fee_scale_size, state, period, parameters) / MONTHS_IN_YEAR
            )
            for i in range(1, tier_count):
                ratio = p.smi_tier_ratios.calc(i)
                threshold = np.floor(monthly_smi * ratio + 0.5)
                tier = tier + (monthly_income > threshold).astype(int)

        exempt = protective | is_tanf | below_fpl_threshold | has_disabled_child

        weekly_copay_per_child = where(
            zero_only_row,
            0,
            p.weekly_amounts.calc(tier + 1),
        )

        # Head Start children have no copay (Section 2.15); only count
        # non-Head-Start eligible children for the copay calculation.
        # Non-Head-Start children are only covered when the unit qualifies
        # through the standard or protective pathway (income + activity
        # or protective services).  Head Start-only units pay $0.
        is_eligible = person("sc_ccap_eligible_child", period)
        is_head_start = person("is_enrolled_in_head_start", period.this_year)
        in_care = person("childcare_hours_per_week", period) > 0
        income_eligible = spm_unit("sc_ccap_income_eligible", period)
        activity_eligible = spm_unit("sc_ccap_activity_eligible", period)
        covers_non_hs = (income_eligible & activity_eligible) | protective
        num_paying = where(
            covers_non_hs,
            spm_unit.sum(is_eligible & ~is_head_start & in_care),
            0,
        )
        uncapped_monthly = (
            weekly_copay_per_child * num_paying * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        )
        # Cap total family copay at 2% of monthly income.
        monthly_income_cap = monthly_income * p.income_cap_rate
        monthly_copay = min_(uncapped_monthly, monthly_income_cap)
        return where(exempt, 0, monthly_copay)
