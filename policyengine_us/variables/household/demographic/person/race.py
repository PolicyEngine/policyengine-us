from policyengine_us.model_api import *


class Race(Enum):
    WHITE = "White, non-Hispanic"
    BLACK = "Black, non-Hispanic"
    HISPANIC = "Hispanic"
    OTHER = "Other"


class race(Variable):
    value_type = Enum
    possible_values = Race
    default_value = Race.WHITE
    entity = Person
    label = "race"
    documentation = "The broadest racial category (White only, Black only, Hispanic, Other)"
    definition_period = YEAR

    def formula(person, period, parameters):
        cps_race = person("cps_race", period)
        hispanic = person("is_hispanic", period)
        return select(
            [
                hispanic,
                (cps_race == 1) & ~hispanic,
                (cps_race == 2) & ~hispanic,
                True,
            ],
            [
                Race.HISPANIC,
                Race.WHITE,
                Race.BLACK,
                Race.OTHER,
            ],
        )
