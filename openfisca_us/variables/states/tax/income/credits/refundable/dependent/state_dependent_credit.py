from openfisca_us.model_api import *


class state_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State dependent credit"
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).states.tax.income.credits.refundable.dependent
        person = tax_unit.members
        state = person.household("state_code_str", period)
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child = age < p.child_age_limit[state]
        elderly = age >= p.elderly_age_limit[state]
        disabled = person("is_disabled", period)
        eligible = dependent & (child | elderly | disabled)
        count_eligible = tax_unit.sum(eligible)
        tax_unit_state = tax_unit.household("state_code_str", period)
        capped_eligible = min_(count_eligible, p.cap[tax_unit_state])
        return capped_eligible * p.amount[tax_unit_state]
