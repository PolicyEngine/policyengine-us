from policyengine_us.model_api import *


class ca_ala_general_assistance_personal_property_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Meets property limit for Alameda County General Assistance"
    defined_for = "in_ala"
    reference = "https://www.alamedacountysocialservices.org/acssa-assets/PDF/GA-Policies/GA-Regulations.pdf#page=23"

    def formula(spm_unit, period, parameters):
        p = parameters(
            period
        ).gov.local.ca.ala.general_assistance.personal_property
        personal_property = add(
            spm_unit, period.this_year, ["personal_property"]
        )
        return personal_property <= p.limit
