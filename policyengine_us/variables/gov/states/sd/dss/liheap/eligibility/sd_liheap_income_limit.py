from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sd_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP annualized income limit"
    defined_for = StateCode.SD
    reference = (
        # Pages 1-5 publish three-month limits for sizes 1-15.
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/SD_BenefitMatrix_2024.pdf#page=1",
        "https://web.archive.org/web/20250114001211/https://dss.sd.gov/economicassistance/energy_weatherization_assistance.aspx",
        "https://dss.sd.gov/economicassistance/energy_weatherization_assistance.aspx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap.income
        # Only citizens and eligible aliens count toward household size.
        size = spm_unit("sd_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1), state_group, period, parameters, year_lag=p.fpg_year_lag
        )
        state = spm_unit.household("state_code_str", period)
        four_person_smi = parameters(period).gov.hhs.smi.amount[state]
        size_share = smi(size, state, period, parameters) / four_person_smi
        smi_limit = np.floor(four_person_smi * p.limits.smi_rate) * size_share
        annual_limit = min_(
            guideline * p.limits.fpg_upper_rate,
            max_(guideline * p.limits.fpg_lower_rate, smi_limit),
        )
        # This inferred ordering matches every FY2024 and published FY2026
        # three-month maximum. Annualize the rounded quarter, not its unrounded
        # annual equivalent. Sizes 11+ carry the FY2024 rule forward; earlier
        # backfilled years are unverified and FY2022 used different rounding.
        # NOTE: FY2026 sources conflict for sizes 4-6. The FY2026 plan, section
        # 2.1, sets 60% of state median income for sizes 4-9:
        # https://liheapch.acf.gov/docs/2026/state-plans/SD_Plan_2026.pdf#page=9
        # Applied to the $111,183 FY2026 state median income, that rate gives
        # three-month limits of $16,677, $19,345 and $22,014 (our derivation).
        # The DSS 2025-2026 published limits cited above are $16,075, $18,825
        # and $21,575 (200% of the 2025 poverty guideline). The model follows DSS.
        limit = 4 * np.floor(annual_limit / 4)
        if p.limits.table.in_effect:
            # The published 2024-2025 limits exceed the rule for sizes 4-7 and
            # follow no consistent rounding, so the printed table applies to
            # the sizes it lists.
            table = p.limits.table.amount
            in_table = size <= table.thresholds[-1]
            limit = where(in_table, 4 * table.calc(size), limit)
        return where(size > 0, limit, 0)
