from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from numpy import ceil


def create_mn_dependent_exemption() -> Reform:
    class mn_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Minnesota exemptions amount"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.revisor.mn.gov/statutes/cite/290.0121"
            "https://www.revenue.state.mn.us/sites/default/files/2025-11/m1-inst-25_0.pdf#page=14"
        )
        defined_for = StateCode.MN

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mn.dependent_exemption
            p_baseline = parameters(period).gov.states.mn.tax.income.exemptions

            person = tax_unit.members
            is_dependent = person("is_tax_unit_dependent", period)

            # Age gate: when in effect, only dependents under the chosen age
            # receive the re-priced exemption; over-age dependents fall back to
            # the baseline per-dependent amount. Without the age limit, every
            # dependent receives the re-priced amount.
            if p.age_limit.in_effect:
                age = person("age", period)
                eligible = is_dependent & (age < p.age_limit.threshold)
            else:
                eligible = is_dependent
            older = is_dependent & ~eligible

            eligible_count = tax_unit.sum(eligible)
            older_count = tax_unit.sum(older)

            # Pre-phase-out exemption base: young (or all) dependents priced at
            # the reform amount, over-age dependents kept at the baseline amount.
            exemptions = eligible_count * p.amount + older_count * p_baseline.amount

            # Preserve the baseline AGI phase-out exactly: scale the total by the
            # same stepped fraction above the filing-status AGI threshold.
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            excess_agi = max_(0, agi - p_baseline.agi_threshold[filing_status])
            steps = ceil(excess_agi / p_baseline.agi_step_size[filing_status])
            offset_fraction = p_baseline.agi_step_fraction * steps
            offset = offset_fraction * exemptions
            return max_(0, exemptions - offset)

    class reform(Reform):
        def apply(self):
            self.update_variable(mn_exemptions)

    return reform


def create_mn_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_mn_dependent_exemption()

    p = parameters.gov.contrib.states.mn.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mn_dependent_exemption()
    else:
        return None


mn_dependent_exemption_reform = create_mn_dependent_exemption_reform_fn(
    None, None, bypass=True
)
