from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class wi_wheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Wisconsin WHEAP annual income limit"
    defined_for = StateCode.WI
    reference = (
        "https://docs.legis.wisconsin.gov/statutes/statutes/16/i/27",
        # Section 3.3.1 and Appendix E.
        # PDF pages 45, 166
        "https://web.archive.org/web/20260428215048/https://energyandhousing.wi.gov/Documents/WHEAP/WheapManual_PY26.pdf#page=45",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/WI_BenefitMatrix_2026.xlsx",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.wi.doa.wheap.eligibility
        size = spm_unit("wi_wheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        # The annual limit approximates the annualized one-month test; twelve
        # times each printed one-month limit is within 4 cents of it.
        limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        return where(size > 0, limit, 0)
