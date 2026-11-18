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
            return federal_eitc * p.match

    class nc_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "North Carolina refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.NC
        # Baseline computes this via `adds`; replacing it with a
        # formula requires clearing the inherited computation mode
        # (the core engine rejects `formula` + `adds`/`subtracts`).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Preserve the baseline refundable credits and ADD the new
            # EITC. Baseline nc_income_tax subtracts nc_refundable_credits
            # and excludes nc_use_tax, so no override of it is needed.
            # See #8775.
            baseline_credits = parameters(
                period
            ).gov.states.nc.tax.income.credits.refundable
            return add(tax_unit, period, list(baseline_credits)) + tax_unit(
                "nc_eitc", period
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(nc_eitc)
            self.update_variable(nc_refundable_credits)

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
