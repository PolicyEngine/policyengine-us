from policyengine_us.model_api import *


class ca_foster_youth_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "California foster youth tax credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.credits.foster_youth
        person = tax_unit.members

        age = person("age", period)

        base_credit = p.age_threshold.calc(age)

        eligible_people = add(tax_unit, period, ["ca_foster_youth_tax_credit_eligible"])

        earned_income = add(tax_unit, period, ["earned_income"])

        excess_earned_income = earned_income - base_credit

        reduction_amount = max_(
            0, excess_earned_income * p.reduction_rate
        )
        #If age_eligible is 0, the amount of fytc should be 0
        person_amount = min_(p.max_amount, earned_income - reduction_amount)

        return person_amount * eligible_people
