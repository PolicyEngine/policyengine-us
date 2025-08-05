from policyengine_us.model_api import *


class ca_ala_general_assistance_base_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alameda County General Assistance base amount"
    definition_period = MONTH
    defined_for = "ala_general_assistance_eligible"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"]) > 0
        p = parameters(period).gov.local.ca.ala.general_assistance
        
        # Base amounts: $336 for single, $548 for couple
        base_amount = where(
            married,
            p.amount.married,
            p.amount.single, 
        )
        
        return base_amount
