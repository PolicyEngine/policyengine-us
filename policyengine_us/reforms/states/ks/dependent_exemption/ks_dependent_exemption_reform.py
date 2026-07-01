from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ks_dependent_exemption() -> Reform:
    class ks_eligible_dependents_count(Variable):
        value_type = int
        entity = TaxUnit
        label = "Kansas eligible dependents count"
        definition_period = YEAR
        defined_for = StateCode.KS

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ks.dependent_exemption

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

    class ks_dependent_exemption(Variable):
        value_type = float
        entity = TaxUnit
        label = "Kansas dependent exemption"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.KS

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ks.dependent_exemption

            dependents_count = tax_unit("ks_eligible_dependents_count", period)
            return dependents_count * p.amount

    class ks_exemptions(Variable):
        value_type = float
        entity = TaxUnit
        label = "Kansas exemptions amount"
        unit = USD
        definition_period = YEAR
        reference = "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/"
        defined_for = StateCode.KS

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ks.tax.income.exemptions

            veteran_exemptions_count = add(
                tax_unit,
                period,
                ["ks_disabled_veteran_exemptions_eligible_person"],
            )
            veterans_exemption_amount = (
                veteran_exemptions_count * p.disabled_veteran.base
            )

            # Separated, age-gated and re-priced dependent exemption.
            dependent_exemption_amount = tax_unit("ks_dependent_exemption", period)

            if p.by_filing_status.in_effect:
                filing_status = tax_unit("filing_status", period)
                base_amount = p.by_filing_status.amount[filing_status]
                head_of_household = (
                    filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD
                )
                head_of_household_additional_amount = (
                    head_of_household * p.by_filing_status.hoh_additional_amount
                )
                # Personal portion excludes the per-dependent exemption. In this
                # regime Kansas provides no per-dependent personal exemption, so
                # over-age dependents fall back to the personal treatment, which
                # is nothing.
                personal_amount = (
                    base_amount
                    + veterans_exemption_amount
                    + head_of_household_additional_amount
                )
                return personal_amount + dependent_exemption_amount

            # Consolidated regime: each person, including dependents, receives the
            # consolidated per-person exemption. Remove eligible dependents from the
            # personal count (their exemption is re-priced separately); over-age
            # dependents remain in the personal count and fall back to the base
            # per-person amount.
            exemptions_count = tax_unit("ks_count_exemptions", period)
            eligible_dependents = tax_unit("ks_eligible_dependents_count", period)
            personal_count = exemptions_count - eligible_dependents
            personal_amount = (
                personal_count * p.consolidated.amount + veterans_exemption_amount
            )
            return personal_amount + dependent_exemption_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(ks_eligible_dependents_count)
            self.update_variable(ks_dependent_exemption)
            self.update_variable(ks_exemptions)

    return reform


def create_ks_dependent_exemption_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ks_dependent_exemption()

    p = parameters.gov.contrib.states.ks.dependent_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ks_dependent_exemption()
    else:
        return None


ks_dependent_exemption_reform = create_ks_dependent_exemption_reform_fn(
    None, None, bypass=True
)
