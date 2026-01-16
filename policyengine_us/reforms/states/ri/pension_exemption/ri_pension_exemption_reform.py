from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_pension_exemption() -> Reform:
    class ri_retirement_income_subtraction_eligible(Variable):
        value_type = bool
        entity = TaxUnit
        label = "Eligible for the Rhode Island retirement income subtraction"
        definition_period = YEAR
        reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
        defined_for = StateCode.RI

        def formula(tax_unit, period, parameters):
            p_reform = parameters(
                period
            ).gov.contrib.states.ri.pension_exemption

            if p_reform.in_effect:
                # Use reform income limits
                income = tax_unit("adjusted_gross_income", period)
                filing_status = tax_unit("filing_status", period)
                older_spouse_birth_year = tax_unit(
                    "older_spouse_birth_year", period
                )

                # Age eligibility still required per the proposal
                p_ss = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.social_security.limit
                age_eligible = older_spouse_birth_year <= p_ss.birth_year

                # Income eligibility uses reform limits
                income_limit = p_reform.income_limit[filing_status]
                income_eligible = income < income_limit

                return age_eligible & income_eligible
            else:
                # Use baseline eligibility logic
                income = tax_unit("adjusted_gross_income", period)
                filing_status = tax_unit("filing_status", period)
                older_spouse_birth_year = tax_unit(
                    "older_spouse_birth_year", period
                )

                p_ss = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.social_security.limit
                age_eligible = older_spouse_birth_year <= p_ss.birth_year

                p_tri = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
                income_eligible = income < p_tri.income_limit[filing_status]

                return age_eligible & income_eligible

    class ri_retirement_income_subtraction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island retirement income subtraction"
        unit = USD
        definition_period = YEAR
        reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
        defined_for = "ri_retirement_income_subtraction_eligible"

        def formula(tax_unit, period, parameters):
            p_reform = parameters(
                period
            ).gov.contrib.states.ri.pension_exemption

            person = tax_unit.members
            taxable_pension = person("taxable_pension_income", period)
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            total_taxable_pension = tax_unit.sum(
                taxable_pension * head_or_spouse
            )

            if p_reform.in_effect:
                # Use reform cap
                return min_(total_taxable_pension, p_reform.cap)
            else:
                # Use baseline cap
                p_baseline = parameters(
                    period
                ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
                return min_(total_taxable_pension, p_baseline.cap)

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_retirement_income_subtraction_eligible)
            self.update_variable(ri_retirement_income_subtraction)

    return reform


def create_ri_pension_exemption_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ri_pension_exemption()

    p = parameters.gov.contrib.states.ri.pension_exemption

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_pension_exemption()
    else:
        return None


ri_pension_exemption = create_ri_pension_exemption_reform(
    None, None, bypass=True
)
