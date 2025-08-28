from policyengine_us.model_api import *


class tx_liheap_priority_group(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP priority group household"
    documentation = (
        "Determines if household qualifies for priority group status"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Check all priority group criteria
        has_elderly = spm_unit("tx_liheap_has_elderly_member", period)
        has_disabled = spm_unit("tx_liheap_has_disabled_member", period)
        has_young_child = spm_unit("tx_liheap_has_young_child", period)
        high_energy_burden = spm_unit("tx_liheap_high_energy_burden", period)

        # Household is priority if it meets any of the criteria
        return (
            has_elderly | has_disabled | has_young_child | high_energy_burden
        )
