from policyengine_us.model_api import *


class ky_personal_tax_credits_aged_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Age eligible for Kentucky personal tax credits"
    documentation = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ky.tax.income.credits.personal

        age_threshold = p.age_eligibility
        is_aged = person("age", period) >= age_threshold

        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse

        return head_or_spouse * is_aged