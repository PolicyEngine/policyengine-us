from policyengine_us.model_api import *


class ss_earnings_test_reduction(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security earnings test reduction"
    documentation = (
        "Reduction in Social Security benefits due to earnings test"
    )
    unit = USD
    defined_for = "ss_earnings_test_applicable"
    reference = (
        "https://www.ssa.gov/OACT/COLA/rtea.html",
        "https://www.law.cornell.edu/uscode/text/42/403#f",
    )

    def formula(person, period, parameters):
        # Get age and FRA for year-of-FRA determination
        age = person("age", period)
        fra_months = person("ss_full_retirement_age_months", period)
        fra_years = fra_months / MONTHS_IN_YEAR

        # Get earnings
        employment_income = person("employment_income", period)
        self_employment_income = person("self_employment_income", period)
        total_earnings = employment_income + self_employment_income

        p = parameters(period).gov.ssa.social_security.earnings_test

        # Check if this is the year person reaches FRA
        year_of_fra = (age < fra_years) & ((age + 1) >= fra_years)

        # Calculate excess earnings using appropriate threshold
        excess_earnings = max_(
            0,
            total_earnings
            - where(
                year_of_fra,
                p.exempt_amount_year_of_fra,
                p.exempt_amount_under_fra,
            ),
        )

        # Calculate reduction using appropriate rate
        reduction = excess_earnings * where(
            year_of_fra,
            p.reduction_rate_year_of_fra,
            p.reduction_rate_under_fra,
        )

        # Get the benefit amount to cap the reduction
        benefit = person("ss_retirement_benefit_before_earnings_test", period)

        # Reduction cannot exceed the benefit
        return min_(reduction, benefit)
