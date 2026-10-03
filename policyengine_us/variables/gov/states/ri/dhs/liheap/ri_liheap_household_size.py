from policyengine_us.model_api import *


class ri_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    definition_period = YEAR
    label = "Rhode Island LIHEAP qualified household size"
    defined_for = StateCode.RI
    reference = "https://ripuc.ri.gov/eventsactions/docket/4290-DHS-DR-PUC%203-6%20attachment%20LIHEAP%20Manual%202020%20-%20Final.pdf#page=12"

    def formula(spm_unit, period, parameters):
        # Section III counts only citizens and qualified noncitizens in size,
        # while income from all members is considered. No SNAP-specific bars.
        return add(spm_unit, period, ["is_citizen_or_legal_immigrant"])
