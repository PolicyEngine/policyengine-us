from openfisca_us.model_api import *


class qualifies_for_elderly_or_disabled_credit(Variable):
    value_type = bool
    entity = Person
    label = "Qualifies for elderly or disabled credit"
    documentation = (
        "Whether this tax unit qualifies for the elderly or disabled credit"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        elderly_disabled = parameters(
            period
        ).gov.irs.credits.elderly_or_disabled
        is_elderly = person("age", period) >= elderly_disabled.age
        return is_elderly | person("retired_on_total_disability", period)
