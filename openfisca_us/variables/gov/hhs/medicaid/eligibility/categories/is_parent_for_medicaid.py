from openfisca_us.model_api import *


class is_parent_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Is a parent or care-taker relative for Medicaid"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396u-1"

    def formula(person, period, parameters):
        is_dependent = person("is_tax_unit_dependent", period)
        has_dependent_in_tax_unit = (
            person.tax_unit("tax_unit_count_dependents", period) > 0
        )
        is_parent = ~is_dependent & has_dependent_in_tax_unit
        ma = parameters(period).hhs.medicaid.eligibility.categories.parent
        income = person("medicaid_income_level", period)
        state = person.household("state_code_str", period)
        income_limit = ma.income_limit[state]
        return is_parent & (income < income_limit)
