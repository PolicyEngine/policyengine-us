from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = (
        "Eligible person for the Delaware elderly or disabled income exclusion"
    )
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(person, period, parameters):
        # First get their filing status.
        filing_status = person.tax_unit(
            "state_filing_status_if_married_filing_separately_on_same_return",
            period,
        )
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        # Get the individual disabled status.\
        disability_eligible = person("is_disabled", period)

        # Get the individual filer's age and eligibility.
        age = person("age", period)
        age_eligible = age >= p.eligibility.age_threshold

        # Get the tax unit income
        earned_income = person("earned_income", period)

        # Determine if filer income is eligible.
        income_threshold = p.eligibility.earned_income_limit[filing_status]
        income_eligible = earned_income < income_threshold

        pre_exclusions_agi = person("de_pre_exclusions_agi", period)
        agi_eligible = (
            pre_exclusions_agi <= p.eligibility.agi_limit[filing_status]
        )

        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return (
            (age_eligible | disability_eligible)
            & income_eligible
            & agi_eligible
            & is_head_or_spouse
        )
