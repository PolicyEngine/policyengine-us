from policyengine_us.model_api import *


class rmd_distribution_period(Variable):
    value_type = float
    entity = Person
    label = "Distribution period for required minimum distributions"
    documentation = "Uniform Lifetime Table period at the age attained this year, or the override; 0 before the first distribution year."
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/401#a_9_C_v",
        "https://www.irs.gov/publications/p590b",
    )

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.irs.retirement_distributions.required_minimum_distributions
        age = person("age", period)
        applicable_age = p.applicable_age.calc(person("birth_year", period))
        required = age >= applicable_age
        # The first distribution year's amount may wait until April 1 of next year.
        first_year_deferred = person("rmd_first_year_deferred", period) & (
            age == applicable_age
        )
        override = person("rmd_distribution_period_override", period)
        table_period = p.uniform_lifetime_table.calc(age)
        distribution_period = where(override > 0, override, table_period)
        return where(required & ~first_year_deferred, distribution_period, 0)
