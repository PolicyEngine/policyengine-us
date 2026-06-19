from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_md_dependent_exemption() -> Reform:
    class md_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Maryland eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.md.dependent_exemption
            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            if p.age_limit.in_effect:
                eligible = is_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_dependent
            return tax_unit.sum(eligible)

    class md_dependent_exemption_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maryland dependent exemption maximum before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.md.dependent_exemption
            count = tax_unit("md_eligible_dependents_count", period)
            # Negative amount is a sentinel meaning "use the baseline per-person
            # AGI-stepped amount" (so in_effect=true at default is a no-op). A
            # value >= 0 applies a flat per-dependent amount instead.
            baseline_per = tax_unit("md_personal_exemption", period)
            per_dependent = where(p.amount < 0, baseline_per, p.amount)
            return count * per_dependent

    class md_dependent_exemption_phaseout(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maryland dependent exemption phaseout amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.md.dependent_exemption
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("adjusted_gross_income", period)
            threshold = p.phaseout.threshold[filing_status]
            excess = max_(agi - threshold, 0)
            return excess * p.phaseout.rate

    class md_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maryland dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("md_dependent_exemption_maximum", period)
            phaseout = tax_unit("md_dependent_exemption_phaseout", period)
            return max_(maximum - phaseout, 0)

    class md_older_dependents_count(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maryland older dependents count"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)
            total_dependents = tax_unit.sum(is_dependent)
            eligible = tax_unit("md_eligible_dependents_count", period)
            return max_(0, total_dependents - eligible)

    class md_total_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "MD total personal exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MD

        def formula(tax_unit, period, parameters):
            # Personal portion keeps the baseline per-person (AGI-stepped)
            # amount; dependents are separated out.
            per_person = tax_unit("md_personal_exemption", period)
            tax_unit_size = tax_unit("tax_unit_size", period)
            dependents = tax_unit("tax_unit_dependents", period)
            older_dependents = tax_unit("md_older_dependents_count", period)
            personal_count = tax_unit_size - dependents + older_dependents
            personal_amount = personal_count * per_person

            dependent_exemption_amount = tax_unit("md_dependent_exemption", period)
            return personal_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(md_eligible_dependents_count)
            self.update_variable(md_dependent_exemption_maximum)
            self.update_variable(md_dependent_exemption_phaseout)
            self.update_variable(md_dependent_exemption)
            self.update_variable(md_older_dependents_count)
            self.update_variable(md_total_personal_exemptions)

    return reform


def create_md_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_md_dependent_exemption()

    p = parameters.gov.contrib.states.md.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_md_dependent_exemption()
    else:
        return None


md_dependent_exemption_reform = create_md_dependent_exemption_reform_fn(
    None, None, bypass=True
)
