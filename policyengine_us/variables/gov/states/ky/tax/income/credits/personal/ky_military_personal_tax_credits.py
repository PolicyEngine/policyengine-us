from policyengine_us.model_api import *


class ky_military_personal_tax_credits(Variable):
    value_type = float
    entity = Person
    label = "Kentucky personal tax credits military service amount"
    reference = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"  # (3) (a)
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.credits.personal.amount
        has_military_income = person("military_service_income", period) > 0
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * has_military_income * p.military
