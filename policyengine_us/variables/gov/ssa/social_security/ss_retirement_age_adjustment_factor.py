from policyengine_us.model_api import *


class ss_retirement_age_adjustment_factor(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Social Security retirement age adjustment factor"
    documentation = (
        "Factor to adjust PIA based on early or delayed "
        "retirement relative to full retirement age"
    )
    unit = "/1"
    reference = (
        "https://www.ssa.gov/OACT/quickcalc/early_late.html",
        "https://www.law.cornell.edu/uscode/text/42/402#q",
        "https://www.law.cornell.edu/uscode/text/42/402#w",
    )

    def formula(person, period, parameters):
        claiming_age = person("ss_claiming_age", period)
        age = person("age", period)
        fra_months = person("ss_full_retirement_age_months", period)

        # Convert claiming age to months
        claiming_age_months = claiming_age * MONTHS_IN_YEAR

        # Calculate months from FRA
        months_from_fra = claiming_age_months - fra_months

        p = parameters(period).gov.ssa.social_security.retirement_age_adjustment

        # Early retirement reduction (when months_from_fra < 0)
        months_early = abs(months_from_fra)
        is_early = months_from_fra < 0

        # Marginal rate scale: 5/9% first 36 months, 5/12% beyond
        total_reduction = p.early_retirement.reduction_rates.calc(months_early)
        early_factor = max_(0, 1 - total_reduction)

        # Delayed retirement credit (when months_from_fra > 0)
        years_delayed = months_from_fra / MONTHS_IN_YEAR
        is_delayed = months_from_fra > 0

        # Cap at maximum delayed years
        years_delayed = min_(years_delayed, p.max_delayed_years)

        # Get birth year for credit rate lookup
        birth_year = period.start.year - age

        # Credit rate by birth year from scale parameter
        credit_rate = p.delayed_retirement.credit_rates.calc(birth_year)
        total_credit = years_delayed * credit_rate
        delayed_factor = 1 + total_credit

        return select(
            [is_early, is_delayed],
            [early_factor, delayed_factor],
            default=1.0,
        )
