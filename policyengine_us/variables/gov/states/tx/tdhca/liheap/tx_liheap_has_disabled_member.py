from policyengine_us.model_api import *


class tx_liheap_has_disabled_member(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP household has disabled member"
    documentation = (
        "Determines if household has a member with disability status"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get disability status of all members
        person = spm_unit.members
        is_disabled = person("is_disabled", period)

        # Check if any member is disabled
        # Use sum to avoid .any() which breaks vectorization
        # If sum > 0, at least one member is disabled
        disabled_count = spm_unit.sum(is_disabled)

        return disabled_count > 0
