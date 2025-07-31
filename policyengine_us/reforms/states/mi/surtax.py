from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_mi_surtax() -> Reform:
    class mi_surtax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan surtax"
        defined_for = StateCode.MI
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            taxable_income = tax_unit("mi_taxable_income", period)
            joint = tax_unit("tax_unit_is_joint", period)
            p = parameters(period).gov.contrib.states.mi.surtax.rate
            return where(
                joint,
                p.joint.calc(taxable_income),
                p.single.calc(taxable_income),
            )

    class mi_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan income tax"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        adds = ["mi_income_tax_before_refundable_credits", "mi_surtax"]
        subtracts = ["mi_refundable_credits"]

    class reform(Reform):
        def apply(self):
            self.update_variable(mi_income_tax)
            self.update_variable(mi_surtax)

    return reform


def create_mi_surtax_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mi_surtax()

    p = parameters.gov.contrib.states.mi.surtax

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mi_surtax()
    else:
        return None


mi_surtax = create_mi_surtax_reform(None, None, bypass=True)
