from policyengine_us.model_api import *


class pr_earned_income_credit_eligible(Variable):
    value_type = bool
    unit = USD
    entity = Person
    label = ""
    definition_period = YEAR
    reference = ""

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.credits.earned_income
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        net_income = person("") # if net_income (interest, child care payments etc.)

        return head_or_spouse & net_income < p.net_income_limit