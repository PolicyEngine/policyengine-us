from policyengine_us.model_api import *


class md_military_retirement_subtraction_amount(Variable):
    value_type = float
    entity = Person
    label = "Maryland military retirement income subtraction per person"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-207",
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=17",
    )

    def formula(person, period, parameters):
        # Md. Code Tax-General § 10-207(q)(1): "military retirement income"
        # includes death benefits received as a result of military service, so
        # Survivor Benefit Plan payments to surviving spouses qualify.
        p = parameters(
            period
        ).gov.states.md.tax.income.agi.subtractions.military_retirement
        age = person("age", period)
        military_retirement_income = person("military_retirement_income", period)
        at_or_above_threshold = age >= p.age_threshold
        cap = where(
            at_or_above_threshold,
            p.max_amount.at_or_above_age_threshold,
            p.max_amount.under_age_threshold,
        )
        return min_(military_retirement_income, cap)
