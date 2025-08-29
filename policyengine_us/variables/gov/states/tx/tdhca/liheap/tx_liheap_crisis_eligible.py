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
        # Crisis assistance is available to all LIHEAP-eligible households
        # who face an energy-related emergency (shutoff notice, broken equipment, etc.)
        # Since we can't determine actual crisis situations from available data,
        # we assume all eligible households could potentially qualify for crisis assistance
        # if they presented with an emergency situation
        return spm_unit("tx_liheap_eligible", period)
