from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class hi_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Hawaii LIHEAP annual income limit"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.HI
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/HI_Plan_2026.pdf#page=8,9",
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/HI_BenefitMatrix_2026.pdf#page=3",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("hi_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        group = spm_unit.household("state_group_str", period)
        p = parameters(period).gov.states.hi.dhs.liheap
        smi_limit = p.eligibility.smi_rate * smi(size, state, period, parameters)
        fpg_limit = p.eligibility.fpg_rate * fpg(
            max_(size, 1),
            group,
            period,
            parameters,
            year_lag=p.fpg_year_lag,
        )
        # The accepted plan specifies percentages. The matrix's projected dollar
        # table has inconsistent rounding and a six-person transcription error;
        # use the policy rates with the requested year's federal guidelines.
        return where(size > 0, max_(smi_limit, fpg_limit), 0)
