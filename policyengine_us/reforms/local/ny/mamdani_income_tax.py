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
            p = parameters(period).gov.local.ny.mamdani_income_tax
            taxable_income = person("nyc_taxable_income", period)
            threshold = p.threshold
            rate = p.rate
            # Apply 2% tax only to income above $1 million threshold
            excess_income = max_(taxable_income - threshold, 0)
            return excess_income * rate


    class reform(Reform):
        def apply(self):
            self.update_variable(nyc_mamdani_income_tax)

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
