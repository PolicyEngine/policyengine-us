from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.al.adeca.liheap.eligibility.al_liheap_income_limit import (
    al_liheap_income_limit_for_lag,
)


class al_liheap_cooling_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Alabama LIHEAP regular cooling annualized income limit"
    defined_for = StateCode.AL
    reference = (
        # Section 3.5: the PY2027 chart, from October 1, 2026, shows the 2026
        # guideline arithmetic, $15,960 x 1.5 = $23,940 a year or $1,995 a
        # month for one person.
        "https://liheapch.acf.gov/docs/2027/state-plans/AL_Plan_2027.pdf#page=12",
        # Section 3.5: ADECA adopts the 2026 guidelines upon release.
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.cooling
        return al_liheap_income_limit_for_lag(
            spm_unit, period, parameters, p.fpg_year_lag
        )
