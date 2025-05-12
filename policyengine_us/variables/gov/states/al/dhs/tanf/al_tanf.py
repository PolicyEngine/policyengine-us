from policyengine_us.model_api import *


class al_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Alabama family assistance (TANF)"
    unit: USD
    defined_for = "al_tanf_eligible"
    definition_period = YEAR
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf
        # First check the family size through spm_unit_size
        family_size = spm_unit("spm_unit_size", period)
        capped_family_size = min_(family_size, p.max_unit_size)

        # Second check the payment standard based on the family size

        payment_standard = p.payment_standard[capped_family_size]

        # Return payment standard
        return payment_standard * MONTHS_IN_YEAR
