from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class sc_liheap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "South Carolina LIHEAP annual income limit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    reference = (
        "https://oeo.sc.gov/managedsites/prd/oeo/documents/2026%20LIHEAP%20State%20Plan.pdf#page=8",
        "https://oeo.sc.gov/managedsites/prd/oeo/liheap.html",
    )

    def formula(spm_unit, period, parameters):
        size = spm_unit("sc_liheap_household_size", period)
        state = spm_unit.household("state_code_str", period)
        p = parameters(period)
        base = p.gov.hhs.smi.amount[state]
        factor = smi(size, state, period, parameters) / base
        # Round the four-person base, then floor after the federal size factor.
        # This inferred order reproduces all eight agency annual limits, including
        # the published size-seven/eight values. It is not a legal rounding rule.
        base_limit = np.floor(
            base * p.gov.states.sc.oeo.liheap.eligibility.smi_rate + 0.5
        )
        return where(size > 0, np.floor(base_limit * factor), 0)
