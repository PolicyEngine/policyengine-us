from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_hi_dependent_exemption() -> Reform:
    class hi_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Hawaii eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.HI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.hi.dependent_exemption

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

    class hi_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Hawaii dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.HI

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.hi.dependent_exemption

            dependents_count = tax_unit("hi_eligible_dependents_count", period)
            return dependents_count * p.amount

    class hi_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Hawaii older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.HI

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "hi_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class hi_regular_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Hawaii regular exemptions"
        unit = USD
        reference = "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
        definition_period = YEAR
        defined_for = StateCode.HI

        def formula(tax_unit, period, parameters):
            exemptions_count = tax_unit("exemptions_count", period)
            p = parameters(period).gov.states.hi.tax.income.exemptions

            # Personal exemptions exclude the dependent portion. Over-age
            # dependents fall back to the personal count.
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("hi_older_dependents_count", period)
            personal_count = exemptions_count - dependents + older_dependents

            # Aged heads and spouses get an extra base exemption (preserved
            # exactly as the baseline computes it).
            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            aged = person("age", period) >= p.aged_threshold
            aged_head_spouse_count = tax_unit.sum(aged & head_or_spouse)

            personal_amount = (personal_count + aged_head_spouse_count) * p.base

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("hi_dependent_exemption", period)

            return personal_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(hi_eligible_dependents_count)
            self.update_variable(hi_dependent_exemption)
            self.update_variable(hi_older_dependents_count)
            self.update_variable(hi_regular_exemptions)

    return reform


def create_hi_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_hi_dependent_exemption()

    p = parameters.gov.contrib.states.hi.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_hi_dependent_exemption()
    else:
        return None


hi_dependent_exemption_reform = create_hi_dependent_exemption_reform_fn(
    None, None, bypass=True
)
