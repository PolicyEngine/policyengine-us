from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ga_dependent_exemption() -> Reform:
    class ga_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Georgia eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ga.dependent_exemption

            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)

            # Apply age limit if in effect.
            if p.age_limit.in_effect:
                age_threshold = p.age_limit.threshold
                eligible_dependents = is_dependent & (age < age_threshold)
            else:
                eligible_dependents = is_dependent

            return tax_unit.sum(eligible_dependents)

    class ga_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.GA

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ga.dependent_exemption

            dependents_count = tax_unit("ga_eligible_dependents_count", period)
            return dependents_count * p.amount

    class ga_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Georgia Exemptions"
        defined_for = StateCode.GA
        unit = USD
        definition_period = YEAR
        reference = (
            "https://apps.dor.ga.gov/FillableForms/PDFViewer/Index?form=2022GA500",
        )

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ga.tax.income.exemptions

            # Separated, age-gated and re-priced dependent exemption. Georgia
            # provides no per-dependent personal exemption, so over-age dependents
            # fall back to the personal treatment, which is nothing.
            dependent_exemptions = tax_unit("ga_dependent_exemption", period)

            if p.personal.availability:
                filing_status = tax_unit("filing_status", period)
                personal_exemptions = p.personal.amount[filing_status]
                return personal_exemptions + dependent_exemptions
            return dependent_exemptions

    class reform(Reform):
        def apply(self):
            self.update_variable(ga_eligible_dependents_count)
            self.update_variable(ga_dependent_exemption)
            self.update_variable(ga_exemptions)

    return reform


def create_ga_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ga_dependent_exemption()

    p = parameters.gov.contrib.states.ga.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ga_dependent_exemption()
    else:
        return None


ga_dependent_exemption_reform = create_ga_dependent_exemption_reform_fn(
    None, None, bypass=True
)
