from policyengine_us.model_api import *


class has_disabled_dependent(Variable):
    # FIXME: What if the person isn't a dependent?
    value_type = bool
    entity = Person
    label = "Is taking care of a person with a disability"
    definition_period = MONTH
    reference = "https://www.congress.gov/bill/119th-congress/house-bill/1/text"

    def formula(person, period, parameters) -> bool:
        is_dependent = person("is_tax_unit_dependent", period)
        is_disabled = person("is_disabled", period)

        return person.tax_unit.any(
            is_dependent & is_disabled
        )
