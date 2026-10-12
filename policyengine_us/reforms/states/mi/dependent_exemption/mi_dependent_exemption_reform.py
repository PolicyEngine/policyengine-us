from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_mi_dependent_exemption() -> Reform:
    class mi_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Michigan eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mi.dependent_exemption

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

    class mi_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mi.dependent_exemption

            dependents_count = tax_unit("mi_eligible_dependents_count", period)
            return dependents_count * p.amount

    class mi_older_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Michigan older dependents count"
        definition_period = YEAR
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "mi_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class mi_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan personal and stillborn exemptions"
        defined_for = StateCode.MI
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.mi.tax.income.exemptions

            # Personal exemptions exclude the dependent portion (head + spouse),
            # plus stillborn children, which remain in the personal portion.
            tax_unit_size = tax_unit("tax_unit_size", period)
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("mi_older_dependents_count", period)
            stillborn_children = tax_unit("tax_unit_stillborn_children", period)
            personal_exemptions_count = (
                tax_unit_size - dependents + older_dependents + stillborn_children
            )
            personal_exemption_amount = personal_exemptions_count * p_base.personal

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("mi_dependent_exemption", period)

            return personal_exemption_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(mi_eligible_dependents_count)
            self.update_variable(mi_dependent_exemption)
            self.update_variable(mi_older_dependents_count)
            self.update_variable(mi_personal_exemptions)

    return reform


def create_mi_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_mi_dependent_exemption()

    p = parameters.gov.contrib.states.mi.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mi_dependent_exemption()
    else:
        return None


mi_dependent_exemption_reform = create_mi_dependent_exemption_reform_fn(
    None, None, bypass=True
)
