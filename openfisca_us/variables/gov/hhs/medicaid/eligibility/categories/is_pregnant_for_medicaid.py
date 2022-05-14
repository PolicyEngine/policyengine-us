from openfisca_us.model_api import *


class is_pregnant_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Is pregnant for Medicaid"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#l_1_A"

    def formula(person, period, parameters):
        ma = parameters(period).hhs.medicaid.eligibility.categories.pregnant
        is_pregnant = person("is_pregnant", period)
        days_postpartum = person("count_days_postpartum", period)
        state = person.household("state_code_str", period)
        max_postpartum_days = ma.postpartum_coverage[state]
        is_covered_as_pregnant = is_pregnant | (
            days_postpartum < max_postpartum_days
        )
        income = person("medicaid_income_level", period)
        income_limit = ma.income_limit[state]
        return is_covered_as_pregnant & (income < income_limit)
