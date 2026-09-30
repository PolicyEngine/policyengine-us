from policyengine_us.model_api import *


class ms_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Mississippi LIHEAP eligible household size"
    defined_for = StateCode.MS
    reference = "https://www.sos.ms.gov/adminsearch/ACCode/00000693c.pdf#page=23"

    def formula(spm_unit, period, parameters):
        # Rule 6.3(B)-(C), printed page 22 / PDF page 23, excludes undocumented
        # non-applicants from size while including their countable income in full.
        # SPM units approximate the household; live-in attendants, boarders, and
        # their separate energy arrangements cannot be resolved with current inputs.
        return add(spm_unit, period, ["is_citizen_or_legal_immigrant"])
