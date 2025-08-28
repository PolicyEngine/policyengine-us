from policyengine_us.model_api import *


class ecpa_child_benefit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "End Child Poverty Act child benefit"
    unit = USD
    documentation = "Universal child benefit under the End Child Poverty Act"
    reference = "placeholder - bill not yet introduced"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

        if not p.in_effect:
            return person("age", period) * 0

        age = person("age", period)
        age_limit = p.child_benefit.age_limit
        is_eligible = age < age_limit

        monthly_amount = p.child_benefit.amount_per_month
        annual_amount = monthly_amount * MONTHS_IN_YEAR

        return is_eligible * annual_amount
