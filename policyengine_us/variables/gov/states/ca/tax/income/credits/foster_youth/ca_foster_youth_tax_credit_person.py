from policyengine_us.model_api import *


class ca_foster_youth_tax_credit_person(Variable):
    value_type = float
    entity = Person
    label = "California foster youth tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-3514.pdf#page=4"
    defined_for = "ca_foster_youth_tax_credit_eligible_person"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth
        age = person("age", period)
        base_credit = p.amount.calc(age)
        earned_income = person.tax_unit("tax_unit_earned_income", period)
        excess_earned_income = max_(earned_income - p.phase_out.start, 0)
        reduction_increments = excess_earned_income / p.phase_out.increment
        reduction_amount = max_(0, reduction_increments * p.phase_out.amount)
        return max_(0, base_credit - reduction_amount)
