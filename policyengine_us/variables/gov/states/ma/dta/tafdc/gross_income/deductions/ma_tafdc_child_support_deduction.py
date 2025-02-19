from policyengine_us.model_api import *


class ma_tafdc_child_support_deduction(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) child support deduction"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/73-how-much-income-can-you-have-and-still-qualify-tafdc"
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        child_support = person("alimony_income", period)
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income.deductions
        return min_(child_support, p.child_support_payments)
