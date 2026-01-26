from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_va_hb979() -> Reform:
    class va_income_tax_before_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Virginia income tax before non-refundable credits"
        unit = USD
        definition_period = YEAR
        reference = "https://law.lis.virginia.gov/vacodefull/title58.1/chapter3/article2/"
        defined_for = StateCode.VA

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("va_taxable_income", period)
            p_baseline = parameters(period).gov.states.va.tax.income.rates
            p_reform = parameters(period).gov.contrib.states.va.hb979

            reform_active = p_reform.in_effect
            reform_tax = p_reform.brackets.calc(taxable_income)
            baseline_tax = p_baseline.calc(taxable_income)

            return where(reform_active, reform_tax, baseline_tax)

    class reform(Reform):
        def apply(self):
            self.update_variable(va_income_tax_before_non_refundable_credits)

    return reform


def create_va_hb979_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_va_hb979()

    p = parameters.gov.contrib.states.va.hb979

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_va_hb979()
    else:
        return None


va_hb979 = create_va_hb979_reform(None, None, bypass=True)
