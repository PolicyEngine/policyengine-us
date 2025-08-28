from policyengine_us.model_api import *


class tx_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP benefit"
    unit = USD
    documentation = (
        "Total Texas LIHEAP benefit including regular and crisis assistance"
    )
    reference = "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf"
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get regular and crisis benefits
        regular_benefit = spm_unit("tx_liheap_regular_benefit", period)
        crisis_benefit = spm_unit("tx_liheap_crisis_benefit", period)

        # Total benefit is sum of regular and crisis assistance
        # Note: In practice, households typically receive either regular OR crisis,
        # but we sum them to represent the maximum possible benefit
        return regular_benefit + crisis_benefit
