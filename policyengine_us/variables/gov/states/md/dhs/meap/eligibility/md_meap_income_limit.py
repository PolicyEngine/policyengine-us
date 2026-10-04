from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class md_meap_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP annual income limit"
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/Income-Guidelines-FY2026-Updated-7.9.2025.pdf",
        "https://liheapch.acf.gov/docs/2026/state-plans/MD_Plan_2026.pdf#page=9",
    )
    documentation = "The published annual 200% FPG amounts control sizes 1-10 rather than the plan's truncated equivalent SMI percentages or its inconsistent additional-member line. Annual inputs are compared with annual limits; the printed monthly amounts are rounded separately. Large-household dollar amounts are calculated from the stated SMI rule, not independently published FY26 dollar rows."

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.eligibility
        size = max_(spm_unit("md_meap_household_size", period), 1)
        state = spm_unit.household("state_code_str", period)
        base = parameters(period).gov.hhs.smi.amount[state]
        factor = smi(size, state, period, parameters) / base
        # Federal 60% SMI table ordering; FY26 publishes the large-household
        # rule, but no dollar rows at sizes 11 and above.
        smi_limit = np.floor(factor * np.floor(base * p.smi_rate))
        poverty_limit = spm_unit("md_meap_fpg", period) * p.fpg_rate
        return where(size >= p.smi_min_size, smi_limit, poverty_limit)
