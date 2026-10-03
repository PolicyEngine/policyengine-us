from policyengine_us.model_api import *


class hi_liheap_household_size(Variable):
    value_type = int
    entity = SPMUnit
    label = "Hawaii LIHEAP qualified household size"
    definition_period = YEAR
    defined_for = StateCode.HI
    reference = (
        "https://humanservices.hawaii.gov/wp-content/uploads/2019/07/Policies-and-Procedures-2020.pdf#page=6",
    )

    def formula(spm_unit, period, parameters):
        # The SPM unit approximates the utility-sharing household. All members'
        # income remains countable, including members excluded from this size.
        # COFA citizens can be represented by an explicit qualified-status flag;
        # the shared immigration enum does not yet distinguish COFA status.
        return spm_unit.sum(spm_unit.members("is_citizen_or_legal_immigrant", period))
