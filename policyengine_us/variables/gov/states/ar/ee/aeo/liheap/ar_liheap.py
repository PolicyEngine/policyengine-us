from policyengine_us.model_api import *


class ar_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Arkansas LIHEAP regular heating benefit"
    defined_for = "ar_liheap_eligible"
    documentation = (
        "Annual regular heating grant from the FY2025 through FY2027 fuel matrices. "
        "Other years use parameter backfilling and are unverified estimates."
    )
    reference = (
        "https://liheapch.acf.gov/docs/2027/state-plans/AR_Plan_2027.pdf#page=11",
        "https://liheapch.acf.gov/docs/2026/state-plans/AR_Plan_2026.pdf#page=11",
    )

    def formula(spm_unit, period, parameters):
        # Regular assistance is a fixed grant, not capped by the reported bill.
        # Unsupported fuel mappings are documented in the matrix variable.
        return spm_unit("ar_liheap_matrix_amount", period)
