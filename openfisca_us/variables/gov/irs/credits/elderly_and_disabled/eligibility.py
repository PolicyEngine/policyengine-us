from openfisca_us.model_api import *


class retired_on_total_disability(Variable):
    value_type = bool
    entity = Person
    label = "Retired on total disability"
    documentation = "Whether this individual has retired on disability, and was permanently and totally disabled when they retired"
    definition_period = YEAR

    # Definition from 26 U.S. Code § 22 - Credit for the elderly and the permanently
    # and totally disabled:

    # An individual is permanently and totally disabled if he is unable to engage
    # in any substantial gainful activity by reason of any medically determinable
    # physical or mental impairment which can be expected to result in death or
    # which has lasted or can be expected to last for a continuous period of not
    # less than 12 months. An individual shall not be considered to be permanently
    # and totally disabled unless he furnishes proof of the existence thereof in
    # such form and manner, and at such times, as the Secretary may require.


class qualifies_for_elderly_or_disabled_credit(Variable):
    value_type = bool
    entity = Person
    label = "Qualifies for elderly or disabled credit"
    documentation = (
        "Whether this tax unit qualifies for the elderly or disabled credit"
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        elderly_disabled = parameters(period).irs.credits.elderly_or_disabled
        is_elderly = person("age", period) >= elderly_disabled.age
        return is_elderly | person("retired_on_total_disability", period)
