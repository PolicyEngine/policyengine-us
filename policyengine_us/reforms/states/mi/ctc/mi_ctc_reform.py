from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_mi_ctc() -> Reform:
    class mi_ctc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI
        reference = "https://legislature.mi.gov/Bills/Bill?ObjectName=2025-HB-4055"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.mi.ctc
            federal_ctc = tax_unit("ctc", period)
            return federal_ctc * p.match

    class mi_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        def formula(tax_unit, period, parameters):
            base_credits = add(
                tax_unit,
                period,
                [
                    "mi_eitc",
                    "mi_home_heating_credit",
                    "mi_homestead_property_tax_credit",
                ],
            )
            mi_ctc_amount = tax_unit("mi_ctc", period)
            return base_credits + mi_ctc_amount

    class reform(Reform):
        def apply(self):
            self.update_variable(mi_ctc)
            self.update_variable(mi_refundable_credits)

    return reform


def create_mi_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_mi_ctc()

    p = parameters.gov.contrib.states.mi.ctc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_mi_ctc()
    else:
        return None


mi_ctc = create_mi_ctc_reform(None, None, bypass=True)
