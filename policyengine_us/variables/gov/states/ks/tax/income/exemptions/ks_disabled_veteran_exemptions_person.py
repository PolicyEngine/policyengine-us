from policyengine_us.model_api import *


class ks_disabled_veteran_exemptions_eligible_person(Variable):
    value_type = float
    entity = Person
    label = "Kansas disabled veteran exemptions for each person"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/"
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        disabled = person("is_permanently_and_totally_disabled", period)
        is_veteran = person("is_veteran", period)

        return p.in_effect * disabled * is_veteran