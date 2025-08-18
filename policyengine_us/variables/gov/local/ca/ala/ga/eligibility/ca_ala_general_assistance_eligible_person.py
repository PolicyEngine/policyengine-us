from policyengine_us.model_api import *


class ca_ala_general_assistance_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Alameda County General Assistance"
    definition_period = MONTH
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=19"

    def formula(person, period, parameters):
        age_eligible = person("ca_ala_general_assistance_age_eligible", period)
        personal_property_eligible = person.spm_unit(
            "ca_ala_general_assistance_personal_property_eligible", period
        )
        immigration_status_eligible = person(
            "ca_ala_general_assistance_immigration_status_eligible", period
        )
        receives_ssi = person("ssi", period) > 0
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return (
            age_eligible
            & personal_property_eligible
            & immigration_status_eligible
            & ~receives_ssi
            & is_head_or_spouse
        )
