from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nc_eitc() -> Reform:
    class nc_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.nc.eitc
            federal_eitc = tax_unit("eitc", period)
            return where(p.in_effect, federal_eitc * p.match, 0)

    class nc_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC

        def formula(tax_unit, period, parameters):
            return tax_unit("nc_eitc", period)

    class nc_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina income tax"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC

        def formula(tax_unit, period, parameters):
            tax_before_credits = add(
                tax_unit, period, ["nc_income_tax_before_credits", "nc_use_tax"]
            )
            non_refundable_credits = tax_unit("nc_non_refundable_credits", period)
            tax_before_refundable = max_(0, tax_before_credits - non_refundable_credits)

            refundable_credits = tax_unit("nc_refundable_credits", period)

            return tax_before_refundable - refundable_credits

    class reform(Reform):
        def apply(self):
            self.update_variable(nc_eitc)
            self.update_variable(nc_refundable_credits)
            self.update_variable(nc_income_tax)

    return reform


def create_nc_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_nc_eitc()

    p = parameters.gov.contrib.states.nc.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nc_eitc()
    else:
        return None


nc_eitc = create_nc_eitc_reform(None, None, bypass=True)
