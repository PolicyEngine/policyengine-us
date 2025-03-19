from policyengine_us.model_api import *


class pr_child_tax_credit_child_eligibility(Variable):
    value_type = int
    entity = Person
    label = "Eligiblity for children to qualify for the Puerto Rico child tax credit"
    definition_period = YEAR
    reference = ""

    def formula(person, period, parameters):
        p = parameters(period).gov.territories.pr.tax.income.credits.child_tax_credit
        age = person("age", period)
        age_eligible = age < p.age_threshold
        is_dependent = person("is_tax_unit_dependent", period)

        return age_eligible & is_dependent