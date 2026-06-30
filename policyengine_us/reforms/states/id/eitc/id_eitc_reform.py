from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_id_eitc() -> Reform:
    class id_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Idaho Earned Income Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ID

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.contrib.states.id.child_poverty_impact_dashboard.eitc
            federal_eitc = tax_unit("eitc", period)
            return federal_eitc * p.match

    class id_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Idaho refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.ID
        # Baseline computes this via `adds`; replacing it with a
        # formula requires clearing the inherited computation mode
        # (the core engine rejects `formula` + `adds`/`subtracts`).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Preserve the state's existing baseline refundable
            # credits and ADD the new EITC. Returning only the EITC
            # deletes the baseline refundable credits (this state
            # has them), flipping the reform's sign. See #8775.
            baseline_credits = parameters(
                period
            ).gov.states.id.tax.income.credits.refundable
            return add(tax_unit, period, list(baseline_credits)) + tax_unit(
                "id_eitc", period
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(id_eitc)
            self.update_variable(id_refundable_credits)

    return reform


def create_id_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_id_eitc()

    p = parameters.gov.contrib.states.id.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        p_at_period = p(current_period)
        if p_at_period.in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_id_eitc()
    else:
        return None


id_eitc = create_id_eitc_reform(None, None, bypass=True)
