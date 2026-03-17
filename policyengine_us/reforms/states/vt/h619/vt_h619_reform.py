from policyengine_us.model_api import *


def create_vt_h619() -> Reform:
    class vt_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Vermont income tax"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.VT

        adds = [
            "vt_income_tax_before_refundable_credits",
            "vt_child_care_contributions",
            "vt_h619_income_tax_surcharge",
        ]
        subtracts = ["vt_refundable_credits"]

    class reform(Reform):
        def apply(self):
            self.update_variable(vt_income_tax)

    return reform


def create_vt_h619_reform(parameters, period, bypass: bool = False):
    # Always return the reform - the in_effect check happens in the variable formula
    return create_vt_h619()


vt_h619 = create_vt_h619_reform(None, None, bypass=True)
