from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_il_dependent_exemption() -> Reform:
    class il_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Illinois dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.IL

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.il.dependent_exemption
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            # Age gate: when in effect, restrict the exemption to dependents
            # under the chosen age; otherwise every dependent qualifies,
            # matching the baseline tax_unit_dependents count.
            if p.age_limit.in_effect:
                age = person("age", period)
                eligible = is_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_dependent
            count = tax_unit.sum(eligible)
            return count * p.amount

    class reform(Reform):
        def apply(self):
            self.update_variable(il_dependent_exemption)

    return reform


def create_il_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_il_dependent_exemption()

    p = parameters.gov.contrib.states.il.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_il_dependent_exemption()
    else:
        return None


il_dependent_exemption_reform = create_il_dependent_exemption_reform_fn(
    None, None, bypass=True
)
