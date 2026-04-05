from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ny_s9110() -> Reform:
    """
    NY Senate Bill S9110 - Personal Income Tax Rate Reform

    Replaces NY Tax Law Section 601 subsections (a), (b), (c), (d) with new
    rate tables for tax years 2026-2035+. Introduces a 0% bracket that phases
    in over 10 years and repeals supplemental tax provisions (d-4 through d-7).

    Reference: https://www.nysenate.gov/legislation/bills/2025/S9110
    """

    class ny_main_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "NY main income tax (S9110 reform)"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NY
        reference = "https://www.nysenate.gov/legislation/bills/2025/S9110"

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("ny_taxable_income", period)
            filing_status = tax_unit("filing_status", period)
            status = filing_status.possible_values

            # Use S9110 reform rates
            rates = parameters(period).gov.contrib.states.ny.s9110.rates

            return select(
                [
                    filing_status == status.SINGLE,
                    filing_status == status.JOINT,
                    filing_status == status.HEAD_OF_HOUSEHOLD,
                    filing_status == status.SURVIVING_SPOUSE,
                    filing_status == status.SEPARATE,
                ],
                [
                    rates.single.calc(taxable_income),
                    rates.joint.calc(taxable_income),
                    rates.head_of_household.calc(taxable_income),
                    rates.surviving_spouse.calc(taxable_income),
                    rates.separate.calc(taxable_income),
                ],
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_main_income_tax)
            self.neutralize_variable("ny_supplemental_tax")

    return reform


def create_ny_s9110_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ny_s9110()

    p = parameters.gov.contrib.states.ny.s9110

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_s9110()
    else:
        return None


ny_s9110 = create_ny_s9110_reform(None, None, bypass=True)
