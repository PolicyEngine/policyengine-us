from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.al.adeca.liheap.al_liheap import (
    al_liheap_award,
)
from policyengine_us.variables.gov.states.al.adeca.liheap.payment.al_liheap_base_payment import (
    al_liheap_chart_amount,
)
from policyengine_us.variables.gov.states.al.adeca.liheap.payment.al_liheap_income_band import (
    al_liheap_income_band_for_limit,
)


class al_liheap_cooling(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP regular cooling assistance"
    documentation = (
        "Verified for FY2025 and FY2026 (the May-September 2025 and 2026 "
        "cooling seasons). Earlier years use model parameter backfilling and "
        "are unverified historical estimates. Later years carry the FY2026 "
        "chart amounts forward."
    )
    defined_for = "al_liheap_cooling_eligible"
    reference = (
        # PDF pages 9, 21-23
        "https://adeca.alabama.gov/wp-content/uploads/FY-2026-LIHEAP-Manual-1.pdf#page=9",
        # PDF pages 12-13: section 3.5 adopts the 2026 guidelines upon release.
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=12",
        # PDF pages 4, 12-13: the FY2025 cooling season, IIJA supplement and
        # $320 to $520 range.
        "https://liheapch.acf.gov/docs/2025/state-plans/AL_Plan_2025.pdf#page=4",
        # The chart effective February 17, 2025, on the 2025 guidelines.
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/AL_BenefitMatrix_Cooling_2026.pdf",
        # Section 3.5: the PY2027 chart, from October 1, 2026, shows the limit
        # and band arithmetic on the 2026 guidelines.
        "https://liheapch.acf.gov/docs/2027/state-plans/AL_Plan_2027.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.payment
        limit = spm_unit("al_liheap_cooling_income_limit", period)
        band = al_liheap_income_band_for_limit(spm_unit, period, limit)
        # Regular Cooling pays the chart's Electric column, whose $320 to
        # $470 range plus the $50 high-need addition is plan section 3.6's
        # $320 to $520 cooling benefit range. One payment per cooling season.
        chart_amount = al_liheap_chart_amount(
            spm_unit, period, parameters, p.base_amount.electricity, band
        )
        # The discretionary $50 high-need addition (manual 6.1.6) requires an
        # agency decision unavailable in existing inputs, as for heating.
        return al_liheap_award(spm_unit, period, parameters, chart_amount)
