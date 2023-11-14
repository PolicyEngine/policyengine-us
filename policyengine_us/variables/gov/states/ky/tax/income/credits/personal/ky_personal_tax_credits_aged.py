from policyengine_us.model_api import *


class ky_personal_tax_credits_aged(Variable):
    value_type = float
    entity = Person
    label = "Kentucky personal tax credits amount for aged filers"
    documentation = (
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=53500"
    )
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ky.tax.income.credits.personal.amount
        age_threshold = p.aged.thresholds[-1]
        is_aged = person("age", period) >= age_threshold
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * is_aged * p.aged.amounts[-1]
