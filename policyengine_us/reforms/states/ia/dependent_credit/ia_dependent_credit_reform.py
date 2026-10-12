from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ia_dependent_credit_reform() -> Reform:
    class ia_exemption_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Iowa exemption credit"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://revenue.iowa.gov/sites/default/files/2021-12/IA6251%2841131%29.pdf",
            "https://revenue.iowa.gov/sites/default/files/2023-01/IA6251%2841131%29.pdf",
        )
        defined_for = StateCode.IA

        def formula(tax_unit, period, parameters):
            # Count adult and dependent exemptions
            adult_count = tax_unit("head_spouse_count", period)
            filing_status = tax_unit("filing_status", period)
            hoh_status = filing_status.possible_values.HEAD_OF_HOUSEHOLD
            hoh_bonus = filing_status == hoh_status
            # Count extra adult exemptions based on being elderly and/or blind
            p = parameters(period).gov.states.ia.tax.income
            exemption = p.credits.exemption
            c = parameters(period).gov.contrib.states.ia.dependent_credit
            elder_head = tax_unit("age_head", period) >= exemption.elderly_age
            elder_spouse = tax_unit("age_spouse", period) >= exemption.elderly_age
            elder_count = elder_head.astype(int) + elder_spouse.astype(int)
            blind_head = tax_unit("blind_head", period)
            blind_spouse = tax_unit("blind_spouse", period)
            blind_count = blind_head.astype(int) + blind_spouse.astype(int)
            additional_count = elder_count + blind_count

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

            return (
                (adult_count + hoh_bonus) * exemption.personal
                + additional_count * exemption.additional
                + eligible_count * c.amount
                + older_count * exemption.dependent
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(ia_exemption_credit)

    return reform


def create_ia_dependent_credit_reform_fn(parameters, period, bypass: bool = False):
    if bypass:
        return create_ia_dependent_credit_reform()

    p = parameters.gov.contrib.states.ia.dependent_credit

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ia_dependent_credit_reform()
    else:
        return None


ia_dependent_credit_reform = create_ia_dependent_credit_reform_fn(
    None, None, bypass=True
)
