from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class il_liheap_income_bracket(Variable):
    value_type = int
    entity = SPMUnit
    label = "Income bracket for IL LIHEAP payment (1-4)"
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = (
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/IL_BenefitMatrix_2024.pdf#page=1",
        # PDF pages 1-2
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/IL_BenefitMatrix_Heat-Cool_2026.pdf#page=1",
        # PDF pages 1-2
        "https://ilvalley-edc.org/wp-content/uploads/2026/06/2027-LIHEAP-Benefit-Matrix-FINAL-20260616.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        income = add(spm_unit, period, ["irs_gross_income"])
        p_il = parameters(period).gov.states.il.dceo.liheap
        if p_il.payment.provider_matrix_in_effect:
            size = spm_unit("spm_unit_size", period)
            geography = spm_unit.household("state_group_str", period)
            guideline = fpg(
                size,
                geography,
                period,
                parameters,
                year_lag=p_il.eligibility.fpg_year_lag,
            )
            monthly_income = max_(income, 0) / MONTHS_IN_YEAR
            # Nearest-dollar guideline shares reproduce the published 30-day
            # band tops. The last payment band also covers state funds
            # above 60% SMI, where its four fuel rows are unchanged in the
            # chart. The chart prints no cash row there, and
            # il_liheap_income_eligible keeps households with heat included
            # in rent on the federal limit.
            band = 1
            for rate in p_il.payment.fpg_band_rates:
                top = np.floor(guideline * rate / MONTHS_IN_YEAR + 0.5)
                band = band + (monthly_income > top)
            return band
        household_fpg = spm_unit("spm_unit_fpg", period)
        income_as_fpg_share = where(household_fpg > 0, income / household_fpg, 0)
        # Clamp negative income to bracket 1 (0-50% FPL).
        pct_fpg = max_(income_as_fpg_share, 0)
        p = parameters(period).gov.states.il.dceo.liheap.payment
        return p.income_bracket.calc(pct_fpg)
