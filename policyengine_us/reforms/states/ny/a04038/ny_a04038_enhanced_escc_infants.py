from policyengine_us.model_api import *


def create_ny_a04038_enhanced_escc_infants() -> Reform:
    """
    NY Assembly Bill A04038 - Enhanced Empire State Child Credit for Infants Act

    Doubles the Empire State Child Credit for qualifying children under age one,
    effective tax year 2026 and thereafter.

    Reference: https://assembly.state.ny.us/leg/?default_fld=&bn=A04038&term=2025
    """

    class ny_ctc_post_2024_base(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York CTC post-2024 base amount"
        documentation = (
            "Base New York CTC amount before phase-out under post-2024 rules"
        )
        unit = USD
        definition_period = YEAR
        reference = (
            "https://assembly.state.ny.us/leg/?default_fld=&bn=A04038&term=2025",
            "https://www.nysenate.gov/legislation/laws/TAX/606",
        )
        defined_for = "ny_ctc_post_2024_eligible"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states.ny.tax.income.credits.ctc
            p_reform = parameters(period).gov.contrib.states.ny.a04038
            person = tax_unit.members
            age = person("age", period)

            # Post-2024 CTC rules (2025-2027)
            qualifies_for_federal_ctc = person("ctc_qualifying_child", period)
            qualifies = qualifies_for_federal_ctc & (age >= p.minimum_age)

            # Calculate base credit amount by age
            credit_by_age = p.post_2024.amount.calc(age)

            # Apply infant multiplier
            multiplier = p_reform.multiplier.calc(age)

            qualifying_credit = qualifies * credit_by_age * multiplier

            return tax_unit.sum(qualifying_credit)

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_ctc_post_2024_base)

    return reform


def create_ny_a04038_enhanced_escc_infants_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_a04038_enhanced_escc_infants()

    p = parameters(period).gov.contrib.states.ny.a04038

    if p.in_effect:
        return create_ny_a04038_enhanced_escc_infants()
    else:
        return None


ny_a04038_enhanced_escc_infants = (
    create_ny_a04038_enhanced_escc_infants_reform(None, None, bypass=True)
)
