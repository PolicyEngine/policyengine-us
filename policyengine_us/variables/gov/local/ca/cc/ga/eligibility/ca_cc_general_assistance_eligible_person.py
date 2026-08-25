from policyengine_us.model_api import *


class ca_cc_general_assistance_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for Contra Costa County General Assistance"
    definition_period = MONTH
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(person, period, parameters):
        age_eligible = person("ca_cc_general_assistance_age_eligible", period)
        personal_property_eligible = person.spm_unit(
            "ca_cc_general_assistance_personal_property_eligible", period
        )
        immigration_status_eligible = person(
            "ca_cc_general_assistance_immigration_status_eligible", period
        )
        # Ineligible if receiving SSI, SSDI, unemployment (UIB), or California
        # State Disability Insurance (SDI). SSDI, UIB, and SDI are YEAR-defined;
        # we read the full annual value with period.this_year and test receipt (> 0).
        # Only SSDI bars eligibility here; Social Security retirement/survivors
        # benefits (the broader `social_security` aggregate) are not a categorical
        # bar -- they instead count toward the gap via the
        # general_assistance.countable_income.sources list.
        receives_categorical = (
            (person("ssi", period) > 0)
            | person("receives_ssi", period)
            | (person("social_security_disability", period.this_year) > 0)
            | (person("unemployment_compensation", period.this_year) > 0)
            | (person("ca_state_disability_insurance", period.this_year) > 0)
        )
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return (
            age_eligible
            & personal_property_eligible
            & immigration_status_eligible
            & ~receives_categorical
            & is_head_or_spouse
        )
