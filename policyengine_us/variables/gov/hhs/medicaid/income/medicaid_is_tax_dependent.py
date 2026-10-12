from policyengine_us.model_api import *


class medicaid_is_tax_dependent(Variable):
    value_type = bool
    entity = Person
    label = (
        "Expected to be claimed as a tax dependent for Medicaid MAGI household rules"
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/cfr/text/42/435.603#f_2"

    def formula(person, period, parameters):
        return (
            person("is_tax_unit_dependent", period)
            | person("claimed_as_dependent_on_another_return", period)
            | person("medicaid_has_known_claiming_tax_unit", period)
        )
