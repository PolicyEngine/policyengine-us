from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ok_refundable_ctc() -> Reform:
    """
    Oklahoma Refundable Child Care/Child Tax Credit Reform

    Converts the Oklahoma Child Care/Child Tax Credit (the greater of 20%
    of the federal CDCC or 5% of the federal CTC) from a nonrefundable
    credit to a refundable credit. By default the credit is nonrefundable
    under 68 O.S. § 2357 ("neither credit shall exceed the tax imposed").
    """

    class ok_refundable_child_care_child_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oklahoma refundable Child Care/Child Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OK

        def formula(tax_unit, period, parameters):
            # `ok_child_care_child_tax_credit` is the worksheet value —
            # uncapped, since the baseline applies the liability limit in
            # `ok_income_tax_before_refundable_credits` — so the full
            # credit is paid as a refund.
            return tax_unit("ok_child_care_child_tax_credit", period)

    class ok_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oklahoma nonrefundable income tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OK
        # The baseline variable computes via `adds`. We replace it with a
        # formula, so clear the inherited computation modes to avoid mixing
        # `formula` with `adds`/`subtracts` (rejected by the core engine).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Sum the baseline nonrefundable list with the Child Care/Child
            # Tax Credit filtered out — it is paid as refundable under this
            # reform. Oklahoma applies a simple (unordered) liability cap
            # downstream in `ok_income_tax_before_refundable_credits`, so a
            # filtered sum is exact.
            credits = parameters(period).gov.states.ok.tax.income.credits.nonrefundable
            filtered = [
                credit
                for credit in list(credits)
                if credit != "ok_child_care_child_tax_credit"
            ]
            return add(tax_unit, period, filtered)

    class ok_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Oklahoma refundable income tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.OK
        # Clear the baseline's `adds` mode (see ok_non_refundable_credits).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Baseline refundable credits (ok_ptc, ok_stc, ok_eitc), resolved
            # from the parameter list, plus the now-refundable Child
            # Care/Child Tax Credit.
            refundable = parameters(period).gov.states.ok.tax.income.credits.refundable
            other_refundable = add(tax_unit, period, refundable)
            refundable_cctc = tax_unit(
                "ok_refundable_child_care_child_tax_credit", period
            )
            return other_refundable + refundable_cctc

    class reform(Reform):
        def apply(self):
            self.update_variable(ok_refundable_child_care_child_tax_credit)
            self.update_variable(ok_non_refundable_credits)
            self.update_variable(ok_refundable_credits)

    return reform


def create_ok_refundable_ctc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ok_refundable_ctc()

    p = parameters.gov.contrib.states.ok.child_poverty_impact_dashboard.ctc

    reform_active = False
    current_period = period_(period)

    for _ in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ok_refundable_ctc()
    else:
        return None


ok_refundable_ctc = create_ok_refundable_ctc_reform(None, None, bypass=True)
