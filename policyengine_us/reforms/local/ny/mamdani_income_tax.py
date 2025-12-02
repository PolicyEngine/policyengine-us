from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nyc_mamdani_income_tax() -> Reform:
    class nyc_mamdani_income_tax(Variable):
        value_type = float
        entity = Person
        label = "Zohran Mamdani NYC income tax"
        unit = USD
        definition_period = YEAR
        defined_for = "in_nyc"

        def formula(person, period, parameters):
            taxable_income = person.tax_unit("nyc_taxable_income", period)
            p = parameters(period).gov.local.ny.mamdani_income_tax
            return p.rate.calc(taxable_income)

    class nyc_income_tax_before_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "NYC income tax before credits"
        unit = USD
        definition_period = YEAR
        defined_for = "in_nyc"

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("nyc_taxable_income", period)
            filing_status = tax_unit("filing_status", period)
            filing_statuses = filing_status.possible_values
            p = parameters(period).gov.local.ny.nyc.tax.income.rates
            regular_tax = select(
                [
                    filing_status == filing_statuses.SINGLE,
                    filing_status == filing_statuses.JOINT,
                    filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                    filing_status == filing_statuses.SURVIVING_SPOUSE,
                    filing_status == filing_statuses.SEPARATE,
                ],
                [
                    p.single.calc(taxable_income),
                    p.joint.calc(taxable_income),
                    p.head_of_household.calc(taxable_income),
                    p.surviving_spouse.calc(taxable_income),
                    p.separate.calc(taxable_income),
                ],
            )
            mamdani_tax = add(tax_unit, period, ["nyc_mamdani_income_tax"])
            return regular_tax + mamdani_tax

    class reform(Reform):
        def apply(self):
            self.update_variable(nyc_mamdani_income_tax)
            self.update_variable(nyc_income_tax_before_credits)

    return reform


def create_nyc_mamdani_income_tax_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_nyc_mamdani_income_tax()

    p = parameters.gov.local.ny.mamdani_income_tax

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nyc_mamdani_income_tax()
    else:
        return None


nyc_mamdani_income_tax = create_nyc_mamdani_income_tax_reform(
    None, None, bypass=True
)
