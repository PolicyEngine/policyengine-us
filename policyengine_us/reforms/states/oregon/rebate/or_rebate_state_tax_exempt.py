from policyengine_us.model_api import *


def create_or_rebate_state_tax_exempt() -> Reform:
    class or_rebate_subtraction(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oregon rebate subtraction"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.ubi_center.basic_income
            if p.taxable:
                return tax_unit("basic_income", period)
            return 0

    class or_income_subtractions(Variable):
        value_type = float
        entity = TaxUnit
        label = "OR income subtractions"
        unit = USD
        definition_period = YEAR
        reference = (
            "https://www.oregon.gov/dor/forms/FormsPubs/form-or-40-inst_101-040-1_2021.pdf#page=13",
            "https://www.oregonlegislature.gov/bills_laws/ors/ors316.html",  # Subsection 316.800
        )
        defined_for = StateCode.OR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.states["or"].tax.income.subtractions
            previous_subtractions = add(tax_unit, period, p.subtractions)
            rebate_subtraction = tax_unit("or_rebate_subtraction", period)
            return previous_subtractions + rebate_subtraction

    class reform(Reform):
        def apply(self):
            self.update_variable(or_income_subtractions)
            self.update_variable(or_rebate_subtraction)

    return reform


def create_or_rebate_state_tax_exempt_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_or_rebate_state_tax_exempt()

    p = parameters(period).gov.contrib.states["or"].rebate

    if p.state_tax_exempt:
        return create_or_rebate_state_tax_exempt()
    else:
        return None


or_rebate_state_tax_exempt = create_or_rebate_state_tax_exempt_reform(
    None, None, bypass=True
)
