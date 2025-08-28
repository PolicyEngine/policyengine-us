from policyengine_us.model_api import *


class boost_payment(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "BOOST Act payment"
    unit = USD
    documentation = "Monthly payments under the BOOST Act for eligible adults"
    reference = "placeholder - bill not yet introduced"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.boost_act

        if not p.in_effect:
            return person("age", period) * 0

        age = person("age", period)
        min_age = p.min_age
        max_age = p.max_age

        is_eligible = (age >= min_age) & (age <= max_age)

        monthly_amount = p.amount
        annual_amount = monthly_amount * MONTHS_IN_YEAR

        return is_eligible * annual_amount
