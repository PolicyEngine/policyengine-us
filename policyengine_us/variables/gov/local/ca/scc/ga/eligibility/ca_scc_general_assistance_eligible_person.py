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
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        # Per GA 202, persons eligible for another federal or state cash aid
        # program (here: CAPI for aged/blind/disabled noncitizens) are not
        # eligible for General Assistance.
        capi_eligible = person("ca_capi_eligible_person", period.this_year)
        # Self-employment is not a categorical bar. Per the GA handbook
        # (02Application/Employment_Termination.htm), a self-employed applicant
        # with income below the GA Maximum Basic Need Rate is eligible if they
        # terminate the self-employment (no sanction; documented via a sworn
        # SCD 101 affidavit) and remain available for work. We assume that
        # no-penalty termination/availability step is met and gate self-employed
        # applicants through the income test instead, consistent with how other
        # CA counties (Alameda, LA, Riverside) treat self-employment as income
        # only.
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return (
            age_eligible
            & personal_property_eligible
            & immigration_status_eligible
            & ~receives_ssi
            & ~capi_eligible
            & is_head_or_spouse
        )
