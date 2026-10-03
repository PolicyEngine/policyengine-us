from policyengine_us.model_api import *


class fl_liheap_categorically_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP categorical income eligibility"
    defined_for = StateCode.FL
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=5",
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=50",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.eligibility
        receipts = add(spm_unit, period, p.categorical_programs, options=[ADD])
        # Positive SNAP, state cash assistance, or SSI is the receipt proxy.
        # A minor's SSI may establish this status even when excluded from income.
        # This waives only the income test, not heating responsibility, residency,
        # or qualified-member requirements, and does not select a benefit band.
        return receipts > 0
