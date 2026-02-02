from policyengine_us.model_api import *


class nv_tanf_earned_income_after_disregard(Variable):
    value_type = float
    entity = Person
    label = "Nevada TANF earned income after work expense disregard"
    unit = USD
    definition_period = MONTH
    reference = "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/TANF/TANF_State_Plan_FINAL%20_Effective_12.31.20.pdf#page=17"
    defined_for = StateCode.NV

    def formula(person, period, parameters):
        # Per Nevada TANF State Plan Section 3.4:
        # Work expense deduction is $90 or 20% of gross earnings,
        # whichever is greater, applied to each employed person.
        p = parameters(
            period
        ).gov.states.nv.dwss.tanf.income.work_expense_disregard
        gross_earned = person("tanf_gross_earned_income", period)

        # Calculate work expense deduction: max of flat amount or percentage
        # This is applied per person, not per household
        flat_deduction = p.flat_amount
        percentage_deduction = gross_earned * p.rate
        work_expense_deduction = max_(flat_deduction, percentage_deduction)

        # NOTE: Nevada has graduated earned income disregards (100%/85%/75%/65%)
        # that decrease over 12 months. PolicyEngine cannot track employment
        # duration, so we apply only the work expense deduction.
        # The max_(_, 0) handles zero-income cases where the flat deduction
        # would otherwise create negative countable income.
        return max_(gross_earned - work_expense_deduction, 0)
