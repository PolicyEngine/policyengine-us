from policyengine_us.model_api import *


class tx_ccs_work_exempt(Variable):
    value_type = bool
    entity = Person
    label = "Texas CCS work requirement exempt"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/texas/40-Tex-Admin-Code-SS-809-50"
    defined_for = StateCode.TX

    def formula(person, period):
        # Exemption 1: Full-time student
        is_full_time_student = person("is_full_time_student", period)

        # Exemption 2: Parent with documented medical disability
        is_disabled = person("is_disabled", period)

        # Exemption 3: Parent caring for a physically or mentally disabled family member
        # This exemption is NOT implemented due to complexity in determining:
        # - Which parent is the designated caregiver
        # - Whether caring for disabled spouse vs disabled child has different implications
        # - Whether both parents can claim exemption or just one
        # Future enhancement could add this with better data on caregiving roles

        return is_full_time_student | is_disabled
