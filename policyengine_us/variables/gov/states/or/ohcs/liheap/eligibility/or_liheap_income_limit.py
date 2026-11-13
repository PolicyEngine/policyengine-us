from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class or_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Oregon LIHEAP income limit"
    unit = USD
    defined_for = StateCode.OR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        # FY2026 federal amounts
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=2",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/PY25%20EA%20Operations%20%20Policy%20Manual-%20FINAL%209-27-24.pdf#page=57",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/2026%20Final%20Energy%20Assistance%20Intake%20Operations%20%26%20Policy%20Manual.pdf#page=77",
        "https://www.oregon.gov/ohcs/energy-weatherization/Documents/manuals/09-23-2027-PY-2027-EA-Operations-Policy-Manual.pdf#page=71",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["or"].ohcs.liheap.eligibility
        # Ceiling reproduces every published limit for program years 2025 to
        # 2027; the manual does not prescribe a rounding rule. The product is
        # rounded to cents in float64 first: float32 0.6 is slightly above 0.6,
        # which lifts a whole-dollar product above the integer and would add $1.
        # hhs_smi uses the requested year's SMI.
        smi = spm_unit("hhs_smi", period).astype(np.float64)
        published = np.ceil(np.round(smi * p.smi_rate, 2))
        # 42 U.S.C. 8624(b)(2)(B) pays no household above the greater of 60% of
        # state median income, in the amounts HHS publishes by household size,
        # and 150% of the poverty guideline. A published amount that rounds
        # above that maximum stops there.
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("spm_unit_size", period)
        state = spm_unit.household("state_code_str", period)
        state_group = spm_unit.household("state_group_str", period)
        smi_maximum = liheap_smi_limit(size, state, p_hhs.smi_limit, period, parameters)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        return min_(published, max_(smi_maximum, guideline * p_hhs.fpg_limit))
