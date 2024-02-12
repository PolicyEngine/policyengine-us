from policyengine_us.model_api import *


class ca_foster_youth_tax_credit_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the California foster youth tax credit"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"
    defined_for = StateCode.CA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth
        eitc_eligible = person("ca_eitc_eligible_person", period)
        in_foster_care = person(
            "ca_was_in_qualifying_foster_care_facility", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return eitc_eligible & in_foster_care & head_or_spouse
