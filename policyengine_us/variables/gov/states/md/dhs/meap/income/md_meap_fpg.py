from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class md_meap_fpg(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Maryland MEAP applicable federal poverty guideline"
    unit = USD
    defined_for = StateCode.MD
    reference = (
        "https://dhs.maryland.gov/documents/OHEP/Advisory%20Board/Income-Guidelines-FY2026-Updated-7.9.2025.pdf",
        "https://liheapch.acf.gov/docs/2025/benefits-matricies/MD_BenefitMatrix_2025.pdf",
    )
    documentation = (
        "The FY2026 limits are twice the 2025 poverty guideline and the FY25 matrix "
        "band tops twice the 2024 guideline, so the guideline of the calendar year "
        "before the model year applies; no sheet states the lag."
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.md.dhs.meap.eligibility
        size = max_(spm_unit("md_meap_household_size", period), 1)
        state_group = spm_unit.household("state_group_str", period)
        return fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
