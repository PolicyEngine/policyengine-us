from policyengine_us.model_api import *


def create_mi_surtax() -> Reform:
    class mi_surtax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan surtax"
        defined_for = StateCode.MI
        unit = USD
        definition_period = YEAR

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mi.surtax
            in_effect = p.in_effect
            taxable_income = tax_unit("mi_taxable_income", period)
            joint = tax_unit("tax_unit_is_joint", period)
            surtax = where(
                joint,
                p.rate.joint.calc(taxable_income),
                p.rate.single.calc(taxable_income),
            )
            return where(in_effect, surtax, 0)

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
    # Always return the reform - the in_effect check happens in the formula
    return create_mi_surtax()


mi_surtax = create_mi_surtax_reform(None, None, bypass=True)
