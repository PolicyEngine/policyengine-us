from policyengine_us.model_api import *


class ky_aged_personal_tax_credits(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Kentucky personal tax credits aged amount"
    documentation = "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500#page=3"
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.credits.personal.amount
        age = person("age", period)
        age_credit_amount = p.aged.calc(age)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * age_credit_amount
