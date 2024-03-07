from policyengine_us.model_api import *


class ca_foster_youth_tax_credit_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California foster youth tax credit"
    definition_period = YEAR
    reference = "https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=RTC&sectionNum=17052.2."
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        was_in_foster_care = person("was_in_foster_care", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return was_in_foster_care & is_head_or_spouse
