from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ca_dependent_credit_reform() -> Reform:
    class ca_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "CA Exemptions"
        defined_for = StateCode.CA
        unit = USD
        definition_period = YEAR
        reference = "https://www.ftb.ca.gov/forms/2021/2021-540.pdf"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ca.tax.income.exemptions
            c = parameters(period).gov.contrib.states.ca.dependent_credit
            agi = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)

            # Calculating phase out amount per credit
            over_agi_threshold = max_(0, agi - p.phase_out.start[filing_status])
            increments = np.ceil(
                over_agi_threshold / p.phase_out.increment[filing_status]
            )
            exemption_reduction = increments * p.phase_out.amount

            # Personal exemptions (unchanged)
            personal_exemption_count = p.personal_scale[filing_status]
            personal_aged_blind_exemption_count = personal_exemption_count + tax_unit(
                "aged_blind_count", period
            )
            personal_aged_blind_exemption = max_(
                0,
                personal_aged_blind_exemption_count * (p.amount - exemption_reduction),
            )

            # Split dependents into age-eligible (re-priced) and over-age
            # (baseline) groups. When the age limit is not in effect every
            # dependent is age-eligible, matching the baseline count.
            person = tax_unit.members
            age = person("age", period)
            is_dependent = person("is_tax_unit_dependent", period)
            if c.age_limit.in_effect:
                eligible = is_dependent & (age < c.age_limit.threshold)
            else:
                eligible = is_dependent
            eligible_count = tax_unit.sum(eligible)
            total_dependents = tax_unit.sum(is_dependent)
            older_count = max_(0, total_dependents - eligible_count)

            # Re-priced dependent credit for age-eligible dependents.
            eligible_dependent_exemption = max_(
                0, eligible_count * (c.amount - exemption_reduction)
            )
            # Over-age dependents keep the baseline dependent exemption amount.
            older_dependent_exemption = max_(
                0, older_count * (p.dependent_amount - exemption_reduction)
            )

            return (
                personal_aged_blind_exemption
                + eligible_dependent_exemption
                + older_dependent_exemption
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(ca_exemptions)

    return reform


def create_ca_dependent_credit_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ca_dependent_credit_reform()

    p = parameters.gov.contrib.states.ca.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ca_dependent_credit_reform()
    else:
        return None


ca_dependent_credit_reform = create_ca_dependent_credit_reform_fn(
    None, None, bypass=True
)
