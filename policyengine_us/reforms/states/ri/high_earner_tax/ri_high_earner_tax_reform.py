from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ri_high_earner_tax() -> Reform:
    class ri_income_tax_before_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Rhode Island income tax before refundable credits"
        defined_for = StateCode.RI
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            income = tax_unit("ri_taxable_income", period)
            p_baseline = parameters(period).gov.states.ri.tax.income.rate
            p_reform = parameters(period).gov.contrib.states.ri.high_earner_tax

            # Use reform brackets if in effect, otherwise use baseline
            reform_active = p_reform.in_effect
            reform_tax = p_reform.brackets.calc(income)
            baseline_tax = p_baseline.calc(income)

            return where(reform_active, reform_tax, baseline_tax)

    class reform(Reform):
        def apply(self):
            self.update_variable(ri_income_tax_before_non_refundable_credits)

    return reform


def create_ri_high_earner_tax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ri_high_earner_tax()

    p = parameters.gov.contrib.states.ri.high_earner_tax

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ri_high_earner_tax()
    else:
        return None


ri_high_earner_tax = create_ri_high_earner_tax_reform(None, None, bypass=True)
