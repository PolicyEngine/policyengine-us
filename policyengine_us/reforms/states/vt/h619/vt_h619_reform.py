from policyengine_us.model_api import *
from policyengine_core.periods import instant
from policyengine_core.periods import period as period_


def create_vt_h619() -> Reform:
    class vt_h619_income_tax_surcharge(Variable):
        value_type = float
        entity = TaxUnit
        definition_period = YEAR
        label = "Vermont H.619 income tax surcharge"
        unit = USD
        reference = "https://legislature.vermont.gov/Documents/2026/Docs/BILLS/H-0619/H-0619%20As%20Introduced.pdf"
        defined_for = StateCode.VT

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.vt.h619.income_tax_surcharge

            # Not a marginal tax - applies to FULL AGI once threshold is crossed
            agi = tax_unit("adjusted_gross_income", period)
            meets_threshold = agi >= p.agi_threshold
            return where(meets_threshold, agi * p.rate, 0)

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
            self.update_variable(vt_h619_income_tax_surcharge)
            self.update_variable(vt_income_tax)

    return reform


def create_vt_h619_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_vt_h619()

    p = parameters.gov.contrib.states.vt.h619.income_tax_surcharge
    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_vt_h619()
    return None


vt_h619 = create_vt_h619_reform(None, None, bypass=True)
