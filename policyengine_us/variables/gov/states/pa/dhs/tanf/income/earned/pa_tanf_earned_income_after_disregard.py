from policyengine_us.model_api import *


class pa_tanf_earned_income_after_disregard(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF earned income after fifty percent disregard"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.94 - Eligibility for TANF earned income deductions"
    documentation = "Earned income after applying the fifty percent disregard to income remaining after the standard deduction and personal care expense deductions. Only 50% of this income counts toward TANF eligibility and benefit calculations. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.94.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.earned_income

        # Income after standard deduction and personal care expenses
        # Note: For now, we're not implementing personal care expenses
        # as they require additional information about incapacitated adults
        # and employment type (full-time vs part-time)
        income_after_std_deduction = person(
            "pa_tanf_earned_income_after_standard_deduction", period
        )

        # Apply the 50% disregard (only count 50% of earned income)
        disregard_rate = p.disregard_rate

        return income_after_std_deduction * (1 - disregard_rate)
