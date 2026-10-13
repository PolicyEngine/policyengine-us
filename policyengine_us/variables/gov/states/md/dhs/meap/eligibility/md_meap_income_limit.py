from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import liheap_smi_limit


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
        # PDF pages 2, 5.
        "https://acf.gov/sites/default/files/documents/ocs/COMM_LIHEAP_IM2025-02_SMIStateTable_Att4.pdf#page=5",
    )
    documentation = (
        "The published annual 200% FPG amounts control sizes 1-10 rather than the "
        "plan's truncated equivalent SMI percentages or its inconsistent "
        "additional-member line. Annual inputs are compared with annual limits; the "
        "printed monthly amounts are rounded separately. Sizes 11 and above use 60% "
        "SMI and reproduce the dollar rows ACF LIHEAP IM 2025-02 Attachment 4 prints "
        "for sizes 7 to 12."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.eligibility
        size = max_(spm_unit("md_meap_household_size", period), 1)
        state = spm_unit.household("state_code_str", period)
        smi_limit = liheap_smi_limit(size, state, p.smi_rate, period, parameters)
        poverty_limit = spm_unit("md_meap_fpg", period) * p.fpg_rate
        return where(size >= p.smi_min_size, smi_limit, poverty_limit)
