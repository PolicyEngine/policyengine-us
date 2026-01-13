from policyengine_us.model_api import *


class ia_tanf_fip_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Iowa FIP payment standard"
    unit = USD
    definition_period = MONTH
    reference = "Iowa Administrative Code 441-41.28"
    documentation = "https://www.law.cornell.edu/regulations/iowa/Iowa-Admin-Code-r-441-41-28"
    defined_for = StateCode.IA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ia.dhs.tanf.fip
        family_size = spm_unit("ia_tanf_fip_family_size", period)

        # Get base payment standard for family size up to 10
        base_size = min_(family_size, 10)
        payment_standard = p.payment_standard[base_size]

        # Add increment for each additional member beyond 10
        additional_members = max_(family_size - 10, 0)
        additional_amount = additional_members * p.payment_standard_additional

        return payment_standard + additional_amount
