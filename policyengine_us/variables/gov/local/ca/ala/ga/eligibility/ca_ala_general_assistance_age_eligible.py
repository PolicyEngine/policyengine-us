from policyengine_us.model_api import *


class ca_ala_general_assistance_age_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible for Alameda County General Assistance based on age requirements"
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=21"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.ala.general_assistance
        age = person("monthly_age", period)

        return age >= p.age_threshold
