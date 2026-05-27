from policyengine_us.model_api import *


class ca_scc_general_assistance_eligible_person(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Eligible person for Santa Clara County General Assistance"
    defined_for = "in_scc"
    reference = "https://stgenssa.sccgov.org/debs/program_handbooks/general_assistance/assets/01Policy/Policy.htm"

    def formula(person, period, parameters):
        age_eligible = person("ca_scc_general_assistance_age_eligible", period)
        personal_property_eligible = person.spm_unit(
            "ca_scc_general_assistance_personal_property_eligible", period
        )
        immigration_status_eligible = person(
            "ca_scc_general_assistance_immigration_status_eligible", period
        )
        receives_ssi = person("ssi", period) > 0
        # Per GA 202, persons eligible for another federal or state cash aid
        # program (here: CAPI for aged/blind/disabled noncitizens) are not
        # eligible for General Assistance.
        capi_eligible = person("ca_capi_eligible_person", period)
        is_self_employed = person("is_self_employed", period.this_year)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return (
            age_eligible
            & personal_property_eligible
            & immigration_status_eligible
            & ~receives_ssi
            & ~capi_eligible
            & ~is_self_employed
            & is_head_or_spouse
        )
