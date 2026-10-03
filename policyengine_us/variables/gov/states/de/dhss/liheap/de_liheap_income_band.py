from policyengine_us.model_api import *


class de_liheap_income_band(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Delaware LIHEAP income band"
    defined_for = StateCode.DE
    reference = "https://liheapch.acf.gov/docs/2026/benefits-matricies/CO_BenefitMatrix_Heating_2026.pdf#page=1"

    def formula(spm_unit, period, parameters):
        rates = parameters(
            period
        ).gov.states.de.dhss.liheap.payment.income_band_upper_rates
        income = spm_unit("de_liheap_countable_income", period)
        # Float32 can round a product just below a whole dollar up before floor
        # (e.g. size six, band seven). Preserve the printed whole-dollar bound.
        limit = spm_unit("de_liheap_income_limit", period).astype(np.float64)
        # The published whole-dollar maximums reproduce all 96 cells. The
        # source does not specify rounding applicant income containing cents.
        return select(
            [income <= np.floor(limit * rate) for rate in rates],
            list(range(1, len(rates) + 1)),
            default=len(rates),
        )
