from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_vt_dependent_exemption() -> Reform:
    class vt_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Vermont eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.VT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.vt.dependent_exemption

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

    class vt_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.vt.dependent_exemption

            dependents_count = tax_unit("vt_eligible_dependents_count", period)
            return dependents_count * p.amount

    class vt_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible_dependent_exemptions = tax_unit(
                "vt_eligible_dependents_count", period
            )
            return max_(0, total_dependents - eligible_dependent_exemptions)

    class vt_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont personal exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.vt.tax.income.exemption
            is_joint = tax_unit("tax_unit_is_joint", period)
            elsewhere_head = tax_unit("head_is_dependent_elsewhere", period)
            elsewhere_spouse = tax_unit("spouse_is_dependent_elsewhere", period)
            eligible_head = (~elsewhere_head).astype(int)
            eligible_spouse = (~elsewhere_spouse).astype(int)
            eligible_count = eligible_head + (eligible_spouse * is_joint)
            # Older dependents fall back to the personal exemption count.
            older_dependents = tax_unit("vt_older_dependents_count", period)
            personal_count = eligible_count + older_dependents
            personal_exemption_amount = personal_count * p_base.personal

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("vt_dependent_exemption", period)

            return personal_exemption_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(vt_eligible_dependents_count)
            self.update_variable(vt_dependent_exemption)
            self.update_variable(vt_older_dependents_count)
            self.update_variable(vt_personal_exemptions)

    return reform


def create_vt_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_vt_dependent_exemption()

    p = parameters.gov.contrib.states.vt.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_vt_dependent_exemption()
    else:
        return None


vt_dependent_exemption_reform = create_vt_dependent_exemption_reform_fn(
    None, None, bypass=True
)
