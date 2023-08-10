from policyengine_us.model_api import *


class de_persons_60_or_over_or_disabled_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged or disabled exclusion"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        # Get members in the tax unit
        person = tax_unit.members

        # Then get the DE blind ir disabled exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.persons_60_or_over_or_disabled

        # Get the individual disabled status.
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)

        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)

        # Get spouse age and eligibility
        age_spouse = tax_unit("age_spouse", period)
        age_spouse_eligible = (age_spouse >= p.threshold.age).astype(int)

        # Determine if individual age is eligible.
        age_head_eligible = (age_head >= p.threshold.age).astype(int)

        # Get the individual filer's income.
        is_head = person("is_tax_unit_head", period)

        # Get the tax unit income
        income = person("earned_income", period)
        head_income = tax_unit.sum(is_head * income)
        total_income = where(
            joint,
            tax_unit("tax_unit_earned_income", period),
            head_income,
        )

        # Determine if filer income is eligible.
        income_threshod = p.threshold.income[filing_status]
        income_eligible = (total_income <= income_threshod).astype(int)

        # Check if the individual's eligiblity.
        head_eligible = (disabled_head | age_head_eligible).astype(int)
        spouse_eligible = (disabled_spouse | age_spouse_eligible).astype(int)
        age_or_disability_eligible = where(
            joint,
            head_eligible & spouse_eligible,
            head_eligible,
        )

        pre_exclsuions_agi = tax_unit("de_pre_exclusions_agi", period)
        agi_eligible = (
            pre_exclsuions_agi <= p.threshold.subtraction[filing_status]
        )

        eligible = age_or_disability_eligible & income_eligible & agi_eligible

        return eligible * p.amount[filing_status]
