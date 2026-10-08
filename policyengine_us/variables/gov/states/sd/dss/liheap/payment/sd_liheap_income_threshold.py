from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class sd_liheap_income_threshold(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "South Dakota LIEAP annualized first-tier income threshold"
    defined_for = StateCode.SD
    reference = (
        # PDF pages 1-5
        "https://liheapch.acf.gov/docs/2024/benefits-matricies/SD_BenefitMatrix_2024.pdf#page=1",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/SD_BenefitMatrix_2026.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.sd.dss.liheap
        # Only citizens and eligible aliens count toward household size.
        size = spm_unit("sd_liheap_household_size", period)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(
            max_(size, 1),
            state_group,
            period,
            parameters,
            year_lag=p.income.fpg_year_lag,
        )
        # Half-up rounding reproduces all FY2022 and FY2024 quarterly Mid
        # thresholds. Carry this latest explicit rule into the FY2026 schedule,
        # which names Mid without printing it. This is a numerical inference,
        # not an express rounding instruction; earlier backfill is unverified.
        quarter_limit = np.floor(guideline * p.payment.income_threshold_rate / 4 + 0.5)
        return where(size > 0, 4 * quarter_limit, 0)
