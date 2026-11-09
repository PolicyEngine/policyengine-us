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
        "https://adeca.alabama.gov/wp-content/uploads/FY27-LIHEAP-State-Plan.pdf#page=53",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/AL_Plan_2026.pdf#page=11",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.adeca.liheap.cooling
        return al_liheap_income_limit_for_lag(
            spm_unit, period, parameters, p.fpg_year_lag
        )
