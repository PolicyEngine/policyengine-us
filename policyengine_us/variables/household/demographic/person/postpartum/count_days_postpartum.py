from policyengine_us.model_api import *


class count_days_postpartum(Variable):
    value_type = float
    entity = Person
    label = "Number of days postpartum"
    unit = "day"
    definition_period = YEAR

    def formula(person, period, parameters):
        under_60_days = person("under_60_days_postpartum", period)
        under_12_months = person("under_12_months_postpartum", period)
        return select(
            [
                under_60_days,
                under_12_months,
                True,
            ],
            [
                0,
                60,
                np.inf,
            ],
        )
