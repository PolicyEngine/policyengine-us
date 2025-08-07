from policyengine_us.model_api import *


class self_employment_tax(Variable):
    value_type = float
    entity = Person
    label = "self-employment tax"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_self_emp_tax:
            return 0
        return add(
            person,
            period,
            [
                "self_employment_social_security_tax",
                "self_employment_medicare_tax",
            ],
        )
