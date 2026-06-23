from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_wi_dependent_exemption() -> Reform:
    class wi_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Wisconsin eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.WI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wi.dependent_exemption

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Apply age limit if in effect
            if p.age_limit.in_effect:
                age_threshold = p.age_limit.threshold
                eligible_dependents = is_dependent & (age < age_threshold)
            else:
                eligible_dependents = is_dependent

            return tax_unit.sum(eligible_dependents)

    class wi_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Wisconsin dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.WI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wi.dependent_exemption

            dependents_count = tax_unit("wi_eligible_dependents_count", period)
            return dependents_count * p.amount

    class wi_older_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Wisconsin older dependents count"
        definition_period = YEAR
        defined_for = StateCode.WI

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "wi_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class wi_base_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Wisconsin base exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.WI

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.wi.tax.income

            # Personal exemptions exclude the dependent portion.
            total_exemptions_count = tax_unit("exemptions_count", period)
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("wi_older_dependents_count", period)
            personal_exemptions_count = (
                total_exemptions_count - dependents + older_dependents
            )
            personal_exemption_amount = (
                personal_exemptions_count * p_base.exemption.base
            )

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("wi_dependent_exemption", period)

            return personal_exemption_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(wi_eligible_dependents_count)
            self.update_variable(wi_dependent_exemption)
            self.update_variable(wi_older_dependents_count)
            self.update_variable(wi_base_exemption)

    return reform


def create_wi_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_wi_dependent_exemption()

    p = parameters.gov.contrib.states.wi.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_wi_dependent_exemption()
    else:
        return None


wi_dependent_exemption_reform = create_wi_dependent_exemption_reform_fn(
    None, None, bypass=True
)
