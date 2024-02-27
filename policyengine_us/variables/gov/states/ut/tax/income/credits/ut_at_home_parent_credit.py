from policyengine_us.model_api import *


class ut_at_home_parent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Utah at-home parent credit"
    unit = USD
    definition_period = YEAR
    defined_for = "ut_at_home_parent_credit_eligibility"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        p = parameters(period).gov.states.ut.tax.income.credits.at_home_parent
        count_children = tax_unit.sum((age < p.max_child_age) & is_dependent)

        return p.amount * count_children
