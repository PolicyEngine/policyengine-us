from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_oh_dependent_exemption() -> Reform:
    class oh_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Ohio eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.oh.dependent_exemption
            person = tax_unit.members
            eligible_person = person("oh_personal_exemptions_eligible_person", period)
            is_dependent = person("is_tax_unit_dependent", period)
            eligible = eligible_person & is_dependent
            if p.age_limit.in_effect:
                eligible = eligible & (person("age", period) < p.age_limit.threshold)
            return tax_unit.sum(eligible)

    class oh_dependent_exemption_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio dependent exemption maximum before phaseout"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.oh.dependent_exemption
            count = tax_unit("oh_eligible_dependents_count", period)
            # Negative amount sentinel = use the discrete MAGI-stepped schedule
            # (no-op default, since the contrib schedule mirrors the baseline);
            # a value >= 0 applies a flat per-dependent amount instead.
            agi = tax_unit("oh_agi", period)
            stepped_per = p.schedule.amount.calc(agi)
            per_dependent = where(p.amount < 0, stepped_per, p.amount)
            return count * per_dependent

    class oh_dependent_exemption_phaseout(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio dependent exemption phaseout amount"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.oh.dependent_exemption
            filing_status = tax_unit("filing_status", period)
            agi = tax_unit("oh_agi", period)
            threshold = p.phaseout.threshold[filing_status]
            return max_(agi - threshold, 0) * p.phaseout.rate

    class oh_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            maximum = tax_unit("oh_dependent_exemption_maximum", period)
            phaseout = tax_unit("oh_dependent_exemption_phaseout", period)
            return max_(maximum - phaseout, 0)

    class oh_personal_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Ohio personal exemptions"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OH

        def formula(tax_unit, period, parameters):
            p_base = parameters(period).gov.states.oh.tax.income.exemptions.personal
            agi = tax_unit("oh_agi", period)
            per_person = p_base.amount.calc(agi)

            # Personal portion = all eligible persons minus the dependents that
            # are separated out (over-age dependents stay in the personal count).
            total_eligible = add(
                tax_unit, period, ["oh_personal_exemptions_eligible_person"]
            )
            eligible_dependents = tax_unit("oh_eligible_dependents_count", period)
            personal_count = total_eligible - eligible_dependents
            personal_amount = personal_count * per_person

            dependent_exemption_amount = tax_unit("oh_dependent_exemption", period)
            return personal_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(oh_eligible_dependents_count)
            self.update_variable(oh_dependent_exemption_maximum)
            self.update_variable(oh_dependent_exemption_phaseout)
            self.update_variable(oh_dependent_exemption)
            self.update_variable(oh_personal_exemptions)

    return reform


def create_oh_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_oh_dependent_exemption()

    p = parameters.gov.contrib.states.oh.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_oh_dependent_exemption()
    else:
        return None


oh_dependent_exemption_reform = create_oh_dependent_exemption_reform_fn(
    None, None, bypass=True
)
