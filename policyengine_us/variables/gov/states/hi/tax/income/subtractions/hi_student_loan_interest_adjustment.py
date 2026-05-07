from policyengine_us.model_api import *


class hi_student_loan_interest_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest adjustment relative to federal AGI"
    unit = USD
    definition_period = YEAR
    default_value = 0
    defined_for = StateCode.HI


class hi_student_loan_interest_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest subtraction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        adjustment = tax_unit("hi_student_loan_interest_adjustment", period)
        return max_(adjustment, 0)


class hi_student_loan_interest_addition(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii student loan interest addition"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        adjustment = tax_unit("hi_student_loan_interest_adjustment", period)
        return max_(0, -adjustment)
