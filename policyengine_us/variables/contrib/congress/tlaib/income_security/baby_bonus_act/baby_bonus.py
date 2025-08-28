from policyengine_us.model_api import *


class baby_bonus(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Baby Bonus Act payment"
    unit = USD
    documentation = "One-time payment for children under 1 year old under the Baby Bonus Act"
    reference = "placeholder - bill not yet introduced"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.baby_bonus_act

        if not p.in_effect:
            return person("age", period) * 0

        age = person("age", period)
        max_age = p.max_child_age
        is_eligible_child = age < max_age

        amount = p.amount

        return is_eligible_child * amount
