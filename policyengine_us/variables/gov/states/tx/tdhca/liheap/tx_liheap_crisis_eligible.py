from policyengine_us.model_api import *


class tx_liheap_crisis_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP crisis assistance eligible"
    documentation = "Determines eligibility for Texas LIHEAP crisis assistance"
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Must meet basic eligibility requirements
        eligible = spm_unit("tx_liheap_eligible", period)

        # Crisis situations include utility shutoff notice or emergency repair needs
        # Since we can't determine actual crisis from available data,
        # we assume crisis eligibility for priority households with high energy burden
        high_energy_burden = spm_unit("tx_liheap_high_energy_burden", period)
        is_priority = spm_unit("tx_liheap_priority_group", period)

        # Crisis eligible if eligible and has high burden or is priority group
        return eligible & (high_energy_burden | is_priority)
