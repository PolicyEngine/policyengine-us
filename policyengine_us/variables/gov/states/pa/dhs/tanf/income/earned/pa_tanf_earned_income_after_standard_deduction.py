from policyengine_us.model_api import *


class pa_tanf_earned_income_after_standard_deduction(Variable):
    value_type = float
    entity = Person
    label = "Pennsylvania TANF earned income after standard deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "55 Pa. Code Section 183.94 - Eligibility for TANF earned income deductions"
    documentation = "Earned income after subtracting the standard $90 deduction from gross earned income. This is the first step in calculating countable earned income. https://www.pacodeandbulletin.gov/Display/pacode?file=/secure/pacode/data/055/chapter183/s183.94.html"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.pa.dhs.tanf.earned_income
        gross_earned = person("pa_tanf_gross_earned_income", period)
        standard_deduction = p.standard_deduction

        # Standard deduction is subtracted from gross earned income
        # Cannot go below zero
        return max_(gross_earned - standard_deduction, 0)
