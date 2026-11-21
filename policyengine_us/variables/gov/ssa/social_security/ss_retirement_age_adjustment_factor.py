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
        is_delayed = months_from_fra > 0

        # Get birth year for credit rate lookup
        birth_year = period.start.year - age

        # Credits accrue only for months before the maximum age (70), except
        # that months before 1984 ran to age 72 (42 USC 402(w)(2)(A),
        # Pub. L. 98-21 sec. 114(c)(2)). A person's ceiling therefore runs
        # to the later of age 70 and the start of 1984, capped at age 72.
        delayed = p.delayed_retirement
        months_at_cutoff = (delayed.max_age_cutoff_year - birth_year) * MONTHS_IN_YEAR
        max_months = min_(
            max_(months_at_cutoff, delayed.max_age * MONTHS_IN_YEAR),
            delayed.max_age_before_1984 * MONTHS_IN_YEAR,
        )
        years_delayed = (
            max_(min_(claiming_age_months, max_months) - fra_months, 0) / MONTHS_IN_YEAR
        )

        # Credit rate by birth year from scale parameter
        credit_rate = p.delayed_retirement.credit_rates.calc(birth_year)
        total_credit = years_delayed * credit_rate
        delayed_factor = 1 + total_credit

        return select(
            [is_early, is_delayed],
            [early_factor, delayed_factor],
            default=1.0,
        )
