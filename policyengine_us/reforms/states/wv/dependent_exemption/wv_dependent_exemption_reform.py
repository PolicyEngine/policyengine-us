from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_wv_dependent_exemption() -> Reform:
    class wv_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "West Virginia eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.WV

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wv.dependent_exemption

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

    class wv_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "West Virginia dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.WV

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.wv.dependent_exemption

            dependents_count = tax_unit("wv_eligible_dependents_count", period)
            return dependents_count * p.amount

    class wv_older_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "West Virginia older dependents count"
        definition_period = YEAR
        defined_for = StateCode.WV

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "wv_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class wv_personal_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "West Virginia personal exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.WV

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.wv.tax.income.exemptions

            # Personal exemptions exclude the dependent portion (head + spouse +
            # any over-age dependents that fall back to the personal count).
            tax_unit_size = tax_unit("tax_unit_size", period)
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("wv_older_dependents_count", period)
            personal_count = tax_unit_size - dependents + older_dependents
            personal_amount = where(
                tax_unit_size == 0,
                p_base.base_personal,
                p_base.personal * personal_count,
            )

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("wv_dependent_exemption", period)

            return personal_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(wv_eligible_dependents_count)
            self.update_variable(wv_dependent_exemption)
            self.update_variable(wv_older_dependents_count)
            self.update_variable(wv_personal_exemption)

    return reform


def create_wv_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_wv_dependent_exemption()

    p = parameters.gov.contrib.states.wv.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_wv_dependent_exemption()
    else:
        return None


wv_dependent_exemption_reform = create_wv_dependent_exemption_reform_fn(
    None, None, bypass=True
)
