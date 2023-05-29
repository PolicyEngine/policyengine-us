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

        # input the age of the head of household (and the spouse if applicable)
        age_head = tax_unit("age_head", period)
        age_spouse = where(single, 0, tax_unit("age_spouse", period))

        AFAGI = tax_unit("va_afagi", period)

        # calculate the number of people eligble for age deduction in a household (people who are 65 and older)
        eligible_count = where(age_head >= p.va_age, 1, 0) + where(
            age_spouse >= p.va_age, 1, 0
        )

        # calculate the number of people age >=84 and is eligible for a full deduction
        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse
        full_deduction_count = sum(
            where(birth_year_head < p.birth_year_limit_for_full_amount, 1, 0),
            where(birth_year_spouse < p.birth_year_limit_for_full_amount, 1, 0),
        )

        maximum_allowable_deduction = p.amount * eligible_count
        exceeded_amount = AFAGI - where(
            joint | separate,
            p.threshold.max[filing_status],
            p.threshold.min[filing_status],
        )
        # If the people eligible for an age deduction do not qualify for a full deduction, the age deduction will be adjusted by a reduction.
        reduction = exceeded_amount * where(
            eligible_count == full_deduction_count, 0, 1
        )

        married_filing_status = where(joint, 1, eligible_count)

        # Special case: for all married taxpayers, the age deduction will differ when filing separately vs. filing jointly.
        age_deduction = (
            maximum_allowable_deduction - reduction
        ) / married_filing_status

        return where(math.isnan(age_deduction), 0, age_deduction)
