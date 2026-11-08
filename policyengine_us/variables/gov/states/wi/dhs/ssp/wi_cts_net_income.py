from policyengine_us.model_api import *


class wi_cts_net_income(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual net countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31"

    def formula(person, period, parameters):
        earned = person("wi_cts_gross_earned_income", period)
        unearned = max_(person("wi_cts_gross_income", period) - earned, 0)
        return person("wi_cts_countable_earned_income", period) + unearned
