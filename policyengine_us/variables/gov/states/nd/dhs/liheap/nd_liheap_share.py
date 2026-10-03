from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class nd_liheap_share(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "North Dakota LIHEAP heating expense share"
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/ND_BenefitMatrix_2026.xlsx",
        "https://www.nd.gov/dhs/policymanuals/415/415_30_10.htm",
    )
    defined_for = StateCode.ND

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nd.dhs.liheap
        size = spm_unit("nd_liheap_household_size", period)
        income = spm_unit("nd_liheap_countable_income", period)
        # The published dollar bands differ from the federal SMI formula.
        # Clip only the table lookup; larger households use their actual size.
        table_size = clip(size, 1, p.maximum_published_size)
        published_limits = p.income_limits[table_size]
        state = spm_unit.household("state_code_str", period)
        state_median_income = smi(size, state, period, parameters)
        # Beyond the published table, statutory SMI percentages are an
        # approximation with unverified state rounding, not a size exclusion.
        limits = [
            where(
                size <= p.maximum_published_size,
                published_limits[str(index)],
                state_median_income * rate,
            )
            for index, rate in enumerate(p.smi_band_limits, start=1)
        ]
        share = select(
            [income <= limit for limit in limits],
            p.shares,
            default=0,
        )
        return where(size > 0, share, 0)
