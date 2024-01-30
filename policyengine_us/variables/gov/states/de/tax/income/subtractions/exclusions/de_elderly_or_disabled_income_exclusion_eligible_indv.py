from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_eligible_indv(Variable):
    value_type = bool
    entity = Person
    label = "Individual Eligibility for the Delaware elderly or disabled income exclusion"
    definition_period = YEAR
    defined_for = "de_can_file_separate_on_same_return"

    def formula(person, period, parameters):
        # First get their filing status.
        filing_status = person.tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        # Get the individual disabled status.\
        disability_eligible = person("is_disabled", period)

        # Get the individual filer's age and eligibility.
        age = person("age", period)
        age_eligible = age > p.eligibility.age_threshold

        # Get the tax unit income
        earned_income = person("earned_income", period)

        # Determine if filer income is eligible.
        income_threshold = p.eligibility.earned_income_limit[filing_status]
        income_eligible = earned_income < income_threshold

        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        agi_eligible = (
            pre_exclusions_agi <= p.eligibility.agi_limit[filing_status]
        )

        return (
            (age_eligible | disability_eligible)
            & income_eligible
            & agi_eligible
        )
