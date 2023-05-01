from policyengine_us.model_api import *


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia age deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.va.tax.income.subtractions
        filing_status = tax_unit("filing_status", period)
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        age_deduction_amount = 0

        AFAGI = tax_unit("AFAGI", period)

        # calcualte the number of people eligble for age deduction in a household
        eligible_count = sum(
            where(age_head > 64, 1, 0) + where(age_spouse > 64, 1, 0)
        )
        # calculate the number of people age >=84 and is eligible for a full deduction
        eightyfour_count = sum(
            where(age_head > 83, 1, 0) + where(age_spouse > 83, 1, 0)
        )
        age_deduction_amount = (
            12_000 * eligible_count
            - (where(eligible_count == eightyfour_count, 0, 1))
            * (
                AFAGI
                - where(filing_status in ("JOINT", "SEPARATE"), 75_000, 50_000)
            )
        ) / where(filing_status == "JOINT", 1, eligible_count)

        return age_deduction_amount
