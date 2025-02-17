from policyengine_us.model_api import *


class ny_pension_exclusion(Variable):
    value_type = float
    entity = Person
    label = "NY pension exclusion"
    unit = USD
    documentation = "Exclusion for pension income for eligible individuals."
    definition_period = YEAR

    def formula(person, period, parameters):
        pension_income = person("pension_income", period)
        age = person("age", period)

        # Fetching values from separate YAML files
        min_age = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion.min_age
        cap = parameters(
            period
        ).gov.states.ny.tax.income.agi.subtractions.pension_exclusion.cap

        meets_age_test = age >= min_age
        deductible_pensions = meets_age_test * min_(pension_income, cap)

        return deductible_pensions
