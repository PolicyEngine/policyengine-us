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
            # Retain the baseline dependent taxpayer test and filing exception.
            is_dependent = person("is_tax_unit_dependent", period) & ~person.tax_unit(
                "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
            )

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
            # Apply the same gate to the older-dependent fallback.
            is_dependent = person("is_tax_unit_dependent", period) & ~person.tax_unit(
                "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
            )
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

            # Count ordinary own exemptions separately from dependent eligibility.
            own_exemptions = tax_unit(
                "head_spouse_count_not_dependent_elsewhere", period
            )
            older_dependents = tax_unit("wv_older_dependents_count", period)
            personal_count = own_exemptions + older_dependents
            personal_amount = p_base.personal * personal_count

            # Add separated dependent exemption.
            dependent_exemption_amount = tax_unit("wv_dependent_exemption", period)

            # Section 11-21-16(d) gives each claimable filer $500 in units
            # without dependent members. Preserve existing allocation otherwise.
            person = tax_unit.members
            claimable_filers = tax_unit.sum(
                person("is_tax_unit_head_or_spouse", period)
                & person("claimable_as_dependent_on_another_return", period)
            )
            filer_allowances = (
                p_base.personal * own_exemptions
                + p_base.base_personal * claimable_filers
            )
            childless_claimable = (tax_unit("tax_unit_dependents", period) == 0) & (
                claimable_filers > 0
            )
            exemptions = tax_unit("exemptions_count", period)
            ordinary_amount = where(
                exemptions == 0,
                p_base.base_personal,
                personal_amount + dependent_exemption_amount,
            )
            return where(childless_claimable, filer_allowances, ordinary_amount)

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
