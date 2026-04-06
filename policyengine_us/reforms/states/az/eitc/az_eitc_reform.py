from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_az_eitc() -> Reform:
    class az_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Arizona Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AZ

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.states.az.child_poverty_impact_dashboard.eitc
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * p.match

    class az_refundable_credits(Variable):
        # NOTE: AZ currently has no baseline refundable credits.
        # If AZ adds refundable credits in baseline, this formula must be updated.
        value_type = float
        entity = TaxUnit
        label = "Arizona refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.AZ

        def formula(tax_unit, period, parameters):
            return tax_unit("az_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(az_eitc)
            self.update_variable(az_refundable_credits)

    return reform


def create_az_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_az_eitc()

    p = parameters.gov.contrib.states.az.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_az_eitc()
    else:
        return None


az_eitc = create_az_eitc_reform(None, None, bypass=True)
