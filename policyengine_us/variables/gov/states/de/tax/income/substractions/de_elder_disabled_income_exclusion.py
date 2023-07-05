from policyengine_us.model_api import *


class de_elderly_or_disabled_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware aged or disabled exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Get members in the tax unit
        person = tax_unit.members

        # single = filing_status == filing_status.possible_values.SINGLE
        # separate = filing_status == filing_status.possible_values.SEPARATE

        # Then get the DE blind ir disabled exemptions part of the parameter tree.
        p = parameters(
            period
        ).gov.states.de.tax.income.substractions.elderly_disabled

        # Get the individual disabled status.
        disabled_head = tax_unit("disabled_head", period)
        disabled_spouse = tax_unit("disabled_spouse", period)

        # Get the individual filer's age.
        age_head = tax_unit("age_head", period)

        # Get spouse age and eligibility
        age_spouse = tax_unit("age_spouse", period)
        age_spouse_eligible = (age_spouse >= p.aged).astype(int)

        # Determine if individual age is eligible.
        age_head_eligible = (age_head >= p.aged).astype(int)

        # Get the individual filer's income.
        is_head = person("is_tax_unit_head", period)
        # Get the tax unit income
        income = person("earned_income", period)
        head_income = tax_unit.sum(is_head * income)
        total_income = where(
            filing_status.possible_values.JOINT,
            tax_unit("tax_unit_earned_income", period),
            head_income,
        )

        # Determine if filer income is eligible.
        income_threshod = p.minimum_income[filing_status]
        income_eligible = (total_income <= income_threshod).astype(int)

        # Get the individual filer's substraction result from Line 10.
        # substraction_head = tax_unit("substraction_head", period)

        # Determine if head of household (filer) is eligible.
        # substraction_head_eligible = (substraction_head <= p.substrsaction_result).astype(int)

        # Check if the individual's eligiblity.
        head_eligible = (disabled_head | age_head_eligible).astype(int)
        spouse_eligible = (disabled_spouse | age_spouse_eligible).astype(int)
        age_or_disability_eligible = where(
            filing_status.possible_values.JOINT,
            head_eligible & spouse_eligible,
            head_eligible,
        )
        # head_eligible = (disabled_head | age_head_eligible | income_head_eligible | substraction_head_eligible).astype(int)

        pre_exclsuions_agi = tax_unit("de_pre_exclusions_agi", period)
        agi_eligible = (
            pre_exclsuions_agi <= p.substraction_result[filing_status]
        )

        eligible = age_or_disability_eligible & income_eligible & agi_eligible
        # Calculate total blind exemption.
        return eligible * p.exclusion_amount[filing_status]
