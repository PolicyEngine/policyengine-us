from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_al_dependent_exemption() -> Reform:
    class al_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Alabama dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AL

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.al.dependent_exemption
            p_base = parameters(period).gov.states.al.tax.income.exemptions
            al_agi = tax_unit("al_agi", period)
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            if p.age_limit.in_effect:
                age = person("age", period)
                eligible = is_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_dependent
            count = tax_unit.sum(eligible)
            per_dependent = where(p.amount < 0, p_base.dependent.calc(al_agi), p.amount)
            return count * per_dependent

    class reform(Reform):
        def apply(self):
            self.update_variable(al_dependent_exemption)

    return reform


def create_al_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_al_dependent_exemption()

    p = parameters.gov.contrib.states.al.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_al_dependent_exemption()
    else:
        return None


al_dependent_exemption_reform = create_al_dependent_exemption_reform_fn(
    None, None, bypass=True
)
