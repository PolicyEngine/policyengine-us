from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ny_a04948_youth_standard_deduction() -> Reform:
    """
    NY Assembly Bill A04948 - Youth Standard Deduction

    Enhanced standard deduction of $10,000 for single filers ages 18-24.
    Effective for taxable years beginning after 2026 (i.e., 2027+).

    Reference: https://www.nysenate.gov/legislation/bills/2025/A4948
    """

    class ny_a04948_youth_standard_deduction_eligible(Variable):
        value_type = bool
        entity = Person
        label = "Eligible for NY A04948 youth enhanced standard deduction"
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/614",
        )
        defined_for = StateCode.NY

        def formula(person, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            youth_std_ded = p.youth_standard_deduction
            min_age = youth_std_ded.min_age
            max_age = youth_std_ded.max_age
            # Age requirements: 18-24
            age = person("age", period)
            age_eligible = (age >= min_age) & (age <= max_age)
            # Cannot be claimed as dependent
            not_dependent = ~person("is_tax_unit_dependent", period)
            # Filing status: must be Single
            filing_status = person.tax_unit("filing_status", period)
            is_single = filing_status == filing_status.possible_values.SINGLE
            # Must be the filer
            is_filer = person("is_tax_unit_head_or_spouse", period)
            return age_eligible & not_dependent & is_single & is_filer

    class ny_a04948_youth_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY A04948 youth enhanced standard deduction"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.nysenate.gov/legislation/bills/2025/A4948",
            "https://www.nysenate.gov/legislation/laws/TAX/614",
        )
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.a04948
            # Check if filer is eligible
            person = tax_unit.members
            eligible = person("ny_a04948_youth_standard_deduction_eligible", period)
            filer_eligible = tax_unit.any(eligible)
            enhanced_deduction = p.youth_standard_deduction.amount
            return where(filer_eligible, enhanced_deduction, 0)

    class ny_standard_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY standard deduction"
        unit = USD
        definition_period = YEAR
        reference = "https://www.nysenate.gov/legislation/laws/TAX/614"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            # Get standard NY standard deduction based on filing status
            dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
            p = parameters(period).gov.states.ny.tax.income.deductions.standard
            filing_status = tax_unit("filing_status", period)
            standard = where(
                dependent_elsewhere,
                p.dependent_elsewhere,
                p.amount[filing_status],
            )
            # Check for youth enhanced standard deduction
            youth_deduction = tax_unit("ny_a04948_youth_standard_deduction", period)
            # Use the greater of standard or youth enhanced deduction
            return max_(standard, youth_deduction)

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_a04948_youth_standard_deduction_eligible)
            self.update_variable(ny_a04948_youth_standard_deduction)
            self.update_variable(ny_standard_deduction)

    return reform


def create_ny_a04948_youth_standard_deduction_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_a04948_youth_standard_deduction()

    p = parameters.gov.contrib.states.ny.a04948.youth_standard_deduction
    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_a04948_youth_standard_deduction()
    return None


ny_a04948_youth_standard_deduction = create_ny_a04948_youth_standard_deduction_reform(
    None, None, bypass=True
)
