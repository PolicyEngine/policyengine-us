from policyengine_us.model_api import *


class ca_foster_youth_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "California foster youth tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_eitc_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth
        person = tax_unit.members
        age = person("age", period)
        eligible_person = person(
            "ca_foster_youth_tax_credit_eligible_person", period
        )
        base_credit = p.amount.calc(age) * eligible_person
        total_base_credit = tax_unit.sum(base_credit) * eitc_eligible
        earned_income = tax_unit("tax_unit_earned_income", period)
        excess_earned_income = max_(earned_income - p.phase_out.start, 0)
        reduction_increments = excess_earned_income / p.phase_out.increment
        reduction_amount = max_(0, reduction_increments * p.phase_out.amount)
        return max_(0, total_base_credit - reduction_amount)
