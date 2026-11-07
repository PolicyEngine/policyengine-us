from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class mo_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Missouri LIHEAP annual income limit"
    documentation = "Twelve times Missouri's monthly income limit, a share of state median income. The HHS LIHEAP limit for the household size, divided by twelve and rounded to the nearest dollar, reproduces the published monthly limits for FFY2026 (sizes 1-20) and FFY2027 (sizes 1-10). For households above ten members, the FFY2027 application adds a rounded $170 a month per additional member; that shorthand runs $1 to $2 a month above the 60% SMI amount for twelve to fifteen members (the federal poverty floor governs from sixteen), and the model keeps the 60% SMI amount of the plan."
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/MO_Plan_2026.pdf#page=8",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/MO_BenefitMatrix_2026.docx",
        "https://dssmanuals.mo.gov/wp-content/uploads/2022/02/liheap-application.pdf#page=1",
        # DSS draft FFY2027 plan (report status "Saved -- with Errors").
        "https://dss.mo.gov/sites/mydss/files/media/pdf/2026/08/liheap-active-ffy2027.pdf#page=8",
    )
    defined_for = StateCode.MO

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mo.dss.liheap.eligibility
        size = spm_unit("mo_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        annual_limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        monthly_limit = np.floor(annual_limit / MONTHS_IN_YEAR + 0.5)
        return monthly_limit * MONTHS_IN_YEAR
