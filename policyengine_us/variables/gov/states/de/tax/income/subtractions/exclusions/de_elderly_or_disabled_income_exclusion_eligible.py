from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Delaware elderly or disabled income exclusion"
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.elderly_or_disabled

        # Get the individual disabled status.
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)

        # Get the individual filer's age and eligibility.
        age_head = tax_unit("age_head", period)
        age_head_eligible = age_head > p.eligibility.age_threshold

        # Get spouse age and eligibility
        age_spouse = tax_unit("age_spouse", period)
        age_spouse_eligible = age_spouse > p.eligibility.age_threshold

        # Get the tax unit income
        earned_income = tax_unit("tax_unit_earned_income", period)

        # Determine if filer income is eligible.
        income_threshold = p.eligibility.earned_income_limit[filing_status]
        income_eligible = earned_income < income_threshold

        # Check the individual's eligibility.
        is_joint = tax_unit("tax_unit_is_joint", period)
        head_eligible = disabled_head | age_head_eligible
        spouse_eligible = disabled_spouse | age_spouse_eligible
        age_or_disability_eligible = where(
            is_joint,
            head_eligible & spouse_eligible,
            head_eligible,
        )

        pre_exclusions_agi = tax_unit("de_pre_exclusions_agi", period)
        agi_eligible = (
            pre_exclusions_agi <= p.eligibility.agi_limit[filing_status]
        )

        return age_or_disability_eligible & income_eligible & agi_eligible
