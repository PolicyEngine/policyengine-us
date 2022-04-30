from openfisca_us.model_api import *


class state_dependent_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "State dependent credit"
    unit = USD
    documentation = "State dependent tax credit"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(period).states.tax.income.credits.refundable.dependent
        state = tax_unit.household("state_code_str", period)
        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child = age < p.child_age_limit[state]
        elderly = age >= p.elderly_age_limit[state]
        disabled = person("is_disabled", period)
        eligible = dependent & (child | elderly | disabled)
        count_eligible = tax_unit.sum(eligible)
        capped_eligible = min_(count_eligible, p.cap[state])
        return capped_eligible * p.amount[state]
        