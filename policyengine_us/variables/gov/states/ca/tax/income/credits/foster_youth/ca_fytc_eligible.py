from policyengine_us.model_api import *


class ca_fytc_eligible(Variable):
    value_type = int
    entity = Person
    label = "Eligible for the California foster youth tax credit"
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth

        age = person("age", period)

        meet_age = p.threshold.calc(age)

        eitc_eligibility = person.tax_unit("ca_eitc_eligible", period)

        in_foster_care = person(
            "ca_in_qualifying_foster_care_facility", period
        )

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return meet_age * eitc_eligibility * in_foster_care * head_or_spouse
