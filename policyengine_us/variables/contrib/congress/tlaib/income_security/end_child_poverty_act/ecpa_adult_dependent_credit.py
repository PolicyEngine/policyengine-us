from policyengine_us.model_api import *


class ecpa_adult_dependent_credit(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "End Child Poverty Act adult dependent credit"
    unit = USD
    documentation = (
        "Credit for adult dependents under the End Child Poverty Act"
    )
    reference = "placeholder - bill not yet introduced"

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.contrib.congress.tlaib.income_security_package.end_child_poverty_act

        if not p.in_effect:
            return person("age", period) * 0

        age = person("age", period)
        min_age = p.adult_dependent_credit.min_age
        is_dependent = person("is_tax_unit_dependent", period)

        is_eligible = (age >= min_age) & is_dependent

        amount = p.adult_dependent_credit.amount

        return is_eligible * amount
