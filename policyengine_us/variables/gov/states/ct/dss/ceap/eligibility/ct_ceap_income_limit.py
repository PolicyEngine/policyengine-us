from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


class ct_ceap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Connecticut CEAP income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://liheapch.acf.gov/docs/2026/benefits-matricies/CT_BenefitMatrix_Heat-Crisis_2026.pdf",
        "https://portal.ct.gov/dss/-/media/departments-and-agencies/dss/winter-heating-assistance/09012026/ffy-27-liheap-allocation-plan.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("ct_ceap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        p = parameters(period)
        # This order reproduces every published FY2026/FY2027 size 1-8 limit;
        # the source prints the amounts but does not specify the rounding order.
        amount = liheap_smi_limit(
            size,
            state,
            p.gov.states.ct.dss.ceap.eligibility.smi_rate,
            period,
            parameters,
        )
        return where(size > 0, amount, 0)
