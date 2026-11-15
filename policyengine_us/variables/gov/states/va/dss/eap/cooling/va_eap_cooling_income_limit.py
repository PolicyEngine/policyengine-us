from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.va.dss.eap.va_eap_income_limit import (
    va_eap_annual_income_limit,
)


class va_eap_cooling_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Virginia EAP cooling assistance annual income limit"
    reference = (
        # PDF pages 28, 120
        "https://www.dss.virginia.gov/media/vdss/benefit-programs/documents/eap/Complete_Manual.pdf#page=28",
        # PDF pages 11-12
        "https://liheapch.acf.gov/docs/2026/state-plans/VA_Plan_2026.pdf#page=11",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/VA_BenefitMatrix_2026.pdf#page=1",
        "https://law.lis.virginia.gov/admincode/title22/agency40/chapter680/section63/",
    )
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        # Plan 3.5: cooling recipients "must meet the same income criteria as
        # established for the Heating Assistance component", with the
        # guideline year adopted each June.
        p = parameters(period).gov.states.va.dss.eap.cooling
        return va_eap_annual_income_limit(spm_unit, period, parameters, p.fpg_year_lag)
