from policyengine_us.model_api import *


class ky_personal_tax_credits_military_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligibility for the Kentucky personal tax credits due to military service income"
    documentation = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    )
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.credits.personal

        is_military = person("military_service_income", period) > 0

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return head_or_spouse * is_military
