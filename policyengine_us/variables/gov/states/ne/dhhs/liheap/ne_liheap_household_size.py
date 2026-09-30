from policyengine_us.model_api import *


class ne_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Nebraska LIHEAP eligible household size"
    defined_for = StateCode.NE
    reference = "https://rules.nebraska.gov/rules?agencyId=37&titleId=231"

    def formula_2026(spm_unit, period, parameters):
        # 476 NAC 2-002.02 excludes members who do not satisfy SNAP's
        # citizenship rules. SPM units approximate energy-purchasing units.
        # LIHEAP-specific program violations and residency fraud are not
        # represented by existing inputs and are not modeled.
        return add(
            spm_unit, period.first_month, ["is_snap_immigration_status_eligible"]
        )
