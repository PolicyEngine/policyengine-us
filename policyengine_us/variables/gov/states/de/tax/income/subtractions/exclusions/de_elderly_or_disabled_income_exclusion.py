from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged or disabled exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.persons_60_or_over_or_disabled

        # Get the individual disabled status.
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)

        # Get the individual filer's age and eligibility.
        age_head = tax_unit("age_head", period)
        age_head_eligible = (age_head >= p.threshold.age).astype(int)

        # Get spouse age and eligibility
        age_spouse = tax_unit("age_spouse", period)
        age_spouse_eligible = (age_spouse >= p.threshold.age).astype(int)

        # Get the tax unit income
        is_joint = tax_unit("tax_unit_is_joint", period)
        head_earnings = tax_unit("head_earned", period)
        spouse_earnings = tax_unit("spouse_earned", period)
        total_income = where(
            is_joint,
            head_earnings + spouse_earnings,
            head_earnings,
        )

        # Determine if filer income is eligible.
        income_threshold = p.max_amount.earned_income[filing_status]
        income_eligible = (total_income <= income_threshold).astype(int)

        # Check the individual's eligiblity.
        head_eligible = (disabled_head | age_head_eligible).astype(int)
        spouse_eligible = (disabled_spouse | age_spouse_eligible).astype(int)
        age_or_disability_eligible = where(
            is_joint,
            head_eligible & spouse_eligible,
            head_eligible,
        )

        pre_exclsuions_agi = tax_unit("de_pre_exclusions_agi", period)
        agi_eligible = pre_exclsuions_agi <= p.max_amount.agi[filing_status]

        eligible = age_or_disability_eligible & income_eligible & agi_eligible

        return eligible * p.amount[filing_status]
