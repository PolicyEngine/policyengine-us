from policyengine_us.model_api import *


class ca_ala_general_assistance_age_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Eligible for Alameda County General Assistance based on age requirements"
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/our-services/Work-and-Money/General-Assistance/index"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance.eligibility
        # Check if head is an adult (18+) or an emancipated minor
        age = add(spm_unit, period, ["age_head"])
        is_adult = age >= p.age_threshold
        
        # For emancipated minors, we'd need additional logic
        # For now, just checking age threshold
        return is_adult
