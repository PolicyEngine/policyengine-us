from policyengine_us.model_api import *
import datetime
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
        # input the age of the head of household (and the spouse if applicable)
        filing_statuses = filing_status.possible_values
        single = filing_status == filing_statuses.SINGLE
        joint = filing_status == filing_statuses.JOINT
        separate = filing_status == filing_statuses.SEPARATE

        age_head = tax_unit("age_head", period)
        age_spouse = where(single, 0, tax_unit("age_spouse", period))

        afagi = tax_unit("va_afagi", period)
        # People who were born on or before the threshold date are eligible for a full deduction
        # threshhold_date = datetime.datetime.strptime(p.va_age_date, "%Y-%m-%d")
        threshhold_year = p.va_age_date

        # calcualte the number of people eligble for age deduction in a household (people who are 65 and older)
        eligible_count = where(age_head >= p.va_age, 1, 0) + where(
            age_spouse >= p.va_age, 1, 0
        )

        # calculate the number of people age >=84 and is eligible for a full deduction
        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse
        full_deduction_count = sum(
            where(birth_year_head < threshhold_year, 1, 0),
            where(birth_year_spouse < threshhold_year, 1, 0),
        )

        maximum_allowable_deduction_amount_adjusted_by_filing_status = (
            p.maximum_allowable_amount * eligible_count
        )
        exceeded_amount = afagi - where(
            joint | separate, p.married_limit, p.single_limit
        )
        married_filing_status = where(
            joint, 1, eligible_count
        )  # The deduction amount for married taxpayers is different when filing jointly vs. separately.
        age_deduction = (
            maximum_allowable_deduction_amount_adjusted_by_filing_status
            - where(eligible_count == full_deduction_count, 0, 1)
            * exceeded_amount
        ) / married_filing_status
        return where(math.isnan(age_deduction), 0, age_deduction)
