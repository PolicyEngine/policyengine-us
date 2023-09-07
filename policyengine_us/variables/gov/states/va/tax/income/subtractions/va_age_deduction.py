from policyengine_us.model_api import *
import math


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia age deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.va.tax.income.subtractions.age_deduction

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        joint = filing_status == filing_statuses.JOINT
        separate = filing_status == filing_statuses.SEPARATE
        single = filing_status == filing_statuses.SINGLE

        age_head = tax_unit("age_head", period)
        age_spouse = where(single, 0, tax_unit("age_spouse", period))
        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse

        afagi = tax_unit("va_afagi", period)

        # Calculate the number of people who are eligible for an age deduction
        head_eligible = age_head >= p.age_minimum
        spouse_eligible = age_spouse >= p.age_minimum
        count_eligible = head_eligible.astype(int) + spouse_eligible.astype(
            int
        )

        # Calculate the number of people eligible for a full age deduction
        head_eligible_for_full_deduction = (
            birth_year_head < p.birth_year_limit_for_full_amount
        )
        spouse_eligible_for_full_deduction = (
            birth_year_spouse < p.birth_year_limit_for_full_amount
        )
        count_eligible_for_full_deduction = (
            head_eligible_for_full_deduction.astype(int)
            + spouse_eligible_for_full_deduction.astype(int)
        )

        # Calculate the maximum allowable deduction amount per filing
        maximum_allowable_deduction = p.amount * count_eligible

        # Calculate the amount that the adjusted federal AGI exceeds the threshold
        excess = max_(afagi - p.threshold[filing_status], 0)

        # Reduce by the entire excess, unless both head and spouse (or head only if single)
        # are eligible for the full deduction
        reduction = excess * where(
            count_eligible == count_eligible_for_full_deduction, 0, 1
        )

        # Special case: for all married taxpayers, the age deduction will differ when filing separately vs. filing jointly.
        divisor = where(
            joint, 1, count_eligible
        )  # divisor is 2 if and only if the couple is married filling seprately, and both are eligible

        # Calculate the age deduction amount for each filing
        age_deduction = (maximum_allowable_deduction - reduction) / divisor

        return where(math.isnan(age_deduction), 0, age_deduction)
