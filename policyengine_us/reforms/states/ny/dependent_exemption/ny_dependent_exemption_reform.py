from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ny_dependent_exemption() -> Reform:
    class ny_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY exemptions"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/616"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.dependent_exemption
            person = tax_unit.members
            is_child_dependent = person("is_child_dependent", period)
            # Age gate: when in effect, restrict the exemption to child
            # dependents under the chosen age; otherwise every child dependent
            # qualifies, matching the baseline tax_unit_child_dependents count.
            if p.age_limit.in_effect:
                age = person("age", period)
                eligible = is_child_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_child_dependent
            # As in the baseline, a return on which a filer (or, if joint,
            # either spouse) can be claimed as a dependent has no dependents
            # (Tax Law 616(a), IRC 152(b)(1)).
            dependent_filer = tax_unit(
                "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
            )
            count = where(dependent_filer, 0, tax_unit.sum(eligible))
            return count * p.amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_exemptions)

    return reform


def create_ny_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ny_dependent_exemption()

    p = parameters.gov.contrib.states.ny.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_dependent_exemption()
    else:
        return None


ny_dependent_exemption_reform = create_ny_dependent_exemption_reform_fn(
    None, None, bypass=True
)
