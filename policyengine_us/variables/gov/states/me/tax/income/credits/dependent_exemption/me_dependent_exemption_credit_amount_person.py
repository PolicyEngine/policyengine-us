from policyengine_us.model_api import *


class me_dependent_exemption_credit_amount_person(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Maine dependent exemption credit amount for each person"
    reference = "https://www.mainelegislature.org/legis/statutes/36/title36sec5219-SS.html"
    definition_period = YEAR
    defined_for = "ctc_qualifying_child"

    def formula(person, period, parameters):
        dependent = person("is_tax_unit_dependent", period)
        p = parameters(
            period
        ).gov.states.me.tax.income.credits.dependent_exemption
        age = person("age", period)
        multiplier = p.multiplier.calc(age)
        return dependent * multiplier * p.amount
