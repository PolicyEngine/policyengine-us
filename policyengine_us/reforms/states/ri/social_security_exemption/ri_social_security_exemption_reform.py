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

            # If reform is in effect, use reform parameters
            if p_reform.in_effect:
                # Check if income limit is repealed (true for 2029+)
                if p_reform.income_limit_applies:
                    # Universal exemption - no age or income limit
                    return True

                # Check age eligibility (only if age requirement applies)
                if p_reform.age_requirement_applies:
                    birth_year = tax_unit("older_spouse_birth_year", period)
                    p_baseline = parameters(
                        period
                    ).gov.states.ri.tax.income.agi.subtractions.social_security.limit
                    age_eligible = birth_year <= p_baseline.birth_year
                else:
                    # Age requirement removed
                    age_eligible = True

                # Check income eligibility using reform income limits
                income = tax_unit("adjusted_gross_income", period)
                filing_status = tax_unit("filing_status", period)
                income_limit = p_reform.income_limit[filing_status]
                income_eligible = income < income_limit

                return age_eligible & income_eligible
            else:
                # Use baseline eligibility logic
                income = tax_unit("adjusted_gross_income", period)
                filing_status = tax_unit("filing_status", period)
                birth_year = tax_unit("older_spouse_birth_year", period)

                p = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

                # Age eligibility
                age_eligible = birth_year <= p.birth_year

                # Income eligibility
                income_limit = p.income[filing_status]
                income_eligible = income < income_limit

                return age_eligible & income_eligible

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

            person = tax_unit.members
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)

            # If reform is in effect and age requirement doesn't apply
            # then all SS is exempt, not just the aged portion
            if p_reform.in_effect and not p_reform.age_requirement_applies:
                # All head/spouse taxable SS is exempt
                taxable_social_security = person(
                    "taxable_social_security", period
                )
                return tax_unit.sum(taxable_social_security * head_or_spouse)
            else:
                # Use baseline calculation - only aged SS is exempt
                birth_year = person("birth_year", period)
                p_baseline = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

                aged = birth_year <= p_baseline.birth_year
                head_or_spouse_aged = head_or_spouse & aged

                total_social_security = person("social_security", period)
                aged_head_or_spouse_ss = tax_unit.sum(
                    total_social_security * head_or_spouse_aged
                )
                head_or_spouse_ss = tax_unit.sum(
                    total_social_security * head_or_spouse
                )

                aged_ss_as_a_percentage_of_total_ss = np.zeros_like(
                    head_or_spouse_ss
                )
                mask = head_or_spouse_ss != 0
                aged_ss_as_a_percentage_of_total_ss[mask] = (
                    aged_head_or_spouse_ss[mask] / head_or_spouse_ss[mask]
                )

                taxable_social_security = person(
                    "taxable_social_security", period
                )
                head_or_spouse_taxable_ss = tax_unit.sum(
                    taxable_social_security * head_or_spouse
                )
                return (
                    head_or_spouse_taxable_ss
                    * aged_ss_as_a_percentage_of_total_ss
                )

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
