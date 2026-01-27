from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_social_security_exemption() -> Reform:
    class ri_social_security_modification_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Rhode Island Social Security Modification"
        definition_period = YEAR
        reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p_reform = parameters(
                period
            ).gov.contrib.states.ri.social_security_exemption
            p_baseline = parameters(
                period
            ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

            # Get inputs
            income = tax_unit("adjusted_gross_income", period)
            filing_status = tax_unit("filing_status", period)
            birth_year = tax_unit("older_spouse_birth_year", period)

            # Baseline eligibility: age + income requirements
            baseline_age_eligible = birth_year <= p_baseline.birth_year
            baseline_income_limit = p_baseline.income[filing_status]
            baseline_income_eligible = income < baseline_income_limit
            baseline_eligible = (
                baseline_age_eligible & baseline_income_eligible
            )

            # Reform eligibility depends on which phase:
            # - income_limit_applies=True: universal exemption (2029+)
            # - age_requirement_applies=False: no age requirement (2027+)
            reform_income_limit = p_reform.income_limit[filing_status]
            reform_income_eligible = income < reform_income_limit
            reform_age_eligible = where(
                p_reform.age_requirement_applies,
                birth_year <= p_baseline.birth_year,
                True,
            )
            reform_eligible_with_limits = (
                reform_age_eligible & reform_income_eligible
            )

            # Universal exemption when income limit is repealed
            reform_eligible = where(
                p_reform.income_limit_applies,
                True,
                reform_eligible_with_limits,
            )

            # Select based on whether reform is in effect
            return where(
                p_reform.in_effect, reform_eligible, baseline_eligible
            )

    class ri_social_security_modification(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island Social Security Modification"
        unit = USD
        definition_period = YEAR
        reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
        defined_for = "ri_social_security_modification_eligible"

        def formula(tax_unit, period, parameters):
            p_reform = parameters(
                period
            ).gov.contrib.states.ri.social_security_exemption
            p_baseline = parameters(
                period
            ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            birth_year = person("birth_year", period)
            taxable_social_security = person("taxable_social_security", period)
            total_social_security = person("social_security", period)

            # Calculate total head/spouse taxable SS (used in reform)
            head_or_spouse_taxable_ss = tax_unit.sum(
                taxable_social_security * head_or_spouse
            )

            # Calculate aged portion (used in baseline and when age req applies)
            aged = birth_year <= p_baseline.birth_year
            head_or_spouse_aged = head_or_spouse & aged

            aged_head_or_spouse_ss = tax_unit.sum(
                total_social_security * head_or_spouse_aged
            )
            head_or_spouse_ss = tax_unit.sum(
                total_social_security * head_or_spouse
            )

            aged_ss_ratio = np.zeros_like(head_or_spouse_ss)
            mask = head_or_spouse_ss != 0
            aged_ss_ratio[mask] = (
                aged_head_or_spouse_ss[mask] / head_or_spouse_ss[mask]
            )

            baseline_amount = head_or_spouse_taxable_ss * aged_ss_ratio

            # Reform amount: all taxable SS when age requirement removed
            reform_amount = where(
                p_reform.age_requirement_applies,
                baseline_amount,
                head_or_spouse_taxable_ss,
            )

            return where(p_reform.in_effect, reform_amount, baseline_amount)

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_social_security_modification_eligible)
            self.update_variable(ri_social_security_modification)

    return reform


def create_ri_social_security_exemption_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ri_social_security_exemption()

    p = parameters.gov.contrib.states.ri.social_security_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_social_security_exemption()
    else:
        return None


ri_social_security_exemption = create_ri_social_security_exemption_reform(
    None, None, bypass=True
)
