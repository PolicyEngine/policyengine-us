from policyengine_us.model_api import *


class id_liheap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Idaho LIHEAP modeled income eligibility"
    definition_period = YEAR
    defined_for = StateCode.ID
    reference = (
        "https://liheapch.acf.gov/docs/2026/state-plans/ID_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.liheap.eligibility
        size = spm_unit("id_liheap_household_size", period)
        income = spm_unit("id_liheap_countable_income", period)
        limit = spm_unit("id_liheap_income_limit", period)
        # SNAP receipt can occur anywhere in the October-September program year.
        snap_period = period.offset(
            p.program_year_start_month - 1 - MONTHS_IN_YEAR, "month"
        )
        receives_snap = spm_unit("snap", snap_period, options=[ADD]) > 0
        # Annual SSI is a stable-current-receipt proxy because the application
        # month is not an input. Any member may establish categorical eligibility.
        receives_ssi = spm_unit.any(spm_unit.members("ssi", period, options=[ADD]) > 0)
        # Means-tested VA receipt also qualifies, but veterans_benefits does not
        # identify that category. This unmodeled route is not a legal exclusion.
        return (size > 0) & ((income <= limit) | receives_snap | receives_ssi)
