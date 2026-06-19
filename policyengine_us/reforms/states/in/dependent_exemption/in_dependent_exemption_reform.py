from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_in_dependent_exemption() -> Reform:
    class in_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Indiana eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.IN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states["in"].dependent_exemption

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

    class in_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Indiana dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.IN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states["in"].dependent_exemption

            dependents_count = tax_unit("in_eligible_dependents_count", period)
            return dependents_count * p.amount

    class in_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Indiana older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.IN

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "in_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class in_base_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Indiana base exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.IN

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states["in"].tax.income.exemptions

            # Personal portion excludes the dependent portion of tax unit size.
            tax_unit_size = tax_unit("tax_unit_size", period)
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("in_older_dependents_count", period)
            personal_count = tax_unit_size - dependents + older_dependents
            personal_exemption_amount = personal_count * p_base.base.amount

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("in_dependent_exemption", period)

            return personal_exemption_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(in_eligible_dependents_count)
            self.update_variable(in_dependent_exemption)
            self.update_variable(in_older_dependents_count)
            self.update_variable(in_base_exemptions)

    return reform


def create_in_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_in_dependent_exemption()

    # ``in`` is a Python keyword, so the contrib node can't be reached with
    # attribute access; the build-time ParameterNode is not subscriptable
    # either, so use getattr.
    p = getattr(parameters.gov.contrib.states, "in").dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_in_dependent_exemption()
    else:
        return None


in_dependent_exemption_reform = create_in_dependent_exemption_reform_fn(
    None, None, bypass=True
)
