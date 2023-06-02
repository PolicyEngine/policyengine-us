from policyengine_us.model_api import *


class nj_pension_retirement_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey Pension/Retirement Exclusion"
    unit = USD
    documentation = "New Jersey pension and retirement excludable amount if eligible (Line 28a)"
    definition_period = YEAR
    reference = "https://www.state.nj.us/treasury/taxation/pdf/current/1040i.pdf#page=21"
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # Get the pension/retirement exclusion portion of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exclusions.retirement

        # Pension/Retirement exclusion available for household head and/or spouse if eligible.
        blind_head = tax_unit("blind_head", period)
        disabled_head = tax_unit("disabled_head", period)
        age_eligible = tax_unit("age_head", period) >= p.age_threshold
        eligible_head = age_eligible | blind_head | disabled_head

        blind_spouse = tax_unit("blind_spouse", period)
        disabled_spouse = tax_unit("disabled_spouse", period)
        age_eligible = tax_unit("age_spouse", period) >= p.age_threshold
        eligible_spouse = age_eligible | blind_spouse | disabled_spouse

        # Calculate the pension/retirement exclusion amount for the head and spouse.
        # This includes social security, interest income, and pension income.
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        social_security = person("taxable_social_security", period)
        interest_income = person("taxable_interest_income", period)
        pension_income = person("taxable_pension_income", period)
        potential_head_exclusion = where(
            is_head,
            social_security + interest_income + pension_income,
            0,
        )
        head_exclusion = eligible_head * potential_head_exclusion

        # Spouse exclusion available if filing jointly.
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        joint = filing_status == status.JOINT
        is_spouse = person("is_tax_unit_spouse", period)
        potential_spouse_exclusion = where(
            is_spouse,
            social_security + interest_income + pension_income,
            0,
        )
        spouse_exclusion = joint * eligible_spouse * potential_spouse_exclusion
        exclusion_amount = head_exclusion + spouse_exclusion

        # Get the total income minus interest and pension income to determine exclusion percentage.
        # Line 27 minus 16b and 20b.
        interest_income = add(tax_unit, period, ["taxable_interest_income"])
        pension_income = add(tax_unit, period, ["taxable_pension_income"])
        agi = tax_unit("adjustable_gross_income", period)
        qualifying_income = agi - interest_income - pension_income

        # Get the exclusion percentage based on filing status and income.
        exclusion_percentage = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.WIDOW,
                filing_status == status.SEPARATE,
            ],
            [
                p.percentage.single.calc(qualifying_income),
                p.percentage.joint.calc(qualifying_income),
                p.percentage.head_of_household.calc(qualifying_income),
                p.percentage.widow.calc(qualifying_income),
                p.percentage.separate.calc(qualifying_income),
            ],
        )

        # Get the maximum exclusion amount based on filing status.
        maximum_exclusion = p.max_amount[filing_status]

        return max_(exclusion_amount * exclusion_percentage, maximum_exclusion)
