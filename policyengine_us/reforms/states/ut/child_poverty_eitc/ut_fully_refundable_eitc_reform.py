from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_us.variables.gov.states.tax.income.non_refundable_credit_cap import (
    ordered_capped_state_non_refundable_credits,
)


def create_ut_fully_refundable_eitc() -> Reform:
    """
    Utah Fully Refundable EITC Reform

    Converts the Utah EITC from a nonrefundable credit to a fully refundable
    credit for ALL filers, including childless filers. This is different from
    the existing ut_refundable_eitc reform which only makes it refundable for
    families with young children.
    """

    class ut_fully_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah fully refundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Use the potential (uncapped) UT EITC so the full credit is paid
            # as a refund; `ut_eitc` is capped at tax liability and would zero
            # out the credit for the low-liability filers refundability is
            # meant to help. `ut_eitc_potential` still applies the W-2 wages
            # cap mandated by Utah Code § 59-10-1044.
            return tax_unit("ut_eitc_potential", period)

    class ut_non_refundable_eitc(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah nonrefundable EITC"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Reform makes EITC fully refundable, so nonrefundable portion is 0
            return 0

    class ut_non_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah non-refundable tax credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT

        def formula(tax_unit, period, parameters):
            # Mirror the baseline's ordered-cap logic but drop ut_eitc from
            # the non-refundable bucket — it's paid as refundable under this
            # reform. A raw `sum - ut_eitc` instead of the ordered walk would
            # overstate the non-refundable total whenever the bucket binds at
            # liability (later credits in the ordered list would no longer
            # see the EITC's slot freed correctly).
            ordered_credits = parameters(
                period
            ).gov.states.ut.tax.income.credits.non_refundable
            filtered_credits = [
                credit for credit in list(ordered_credits) if credit != "ut_eitc"
            ]
            return ordered_capped_state_non_refundable_credits(
                tax_unit,
                period,
                filtered_credits,
                "ut_income_tax_before_non_refundable_credits",
            )

    class ut_refundable_credits(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah refundable credits"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.UT
        # The baseline variable computes via `adds`. We replace it with a
        # formula, so clear the inherited computation modes to avoid mixing
        # `formula` with `adds`/`subtracts` (rejected by the core engine).
        adds = None
        subtracts = None

        def formula(tax_unit, period, parameters):
            # Add the fully refundable EITC (positive when reform is in effect)
            return tax_unit("ut_fully_refundable_eitc", period)

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_fully_refundable_eitc)
            self.update_variable(ut_non_refundable_eitc)
            self.update_variable(ut_non_refundable_credits)
            self.update_variable(ut_refundable_credits)

    return reform


def create_ut_fully_refundable_eitc_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_fully_refundable_eitc()

    p = parameters.gov.contrib.states.ut.child_poverty_impact_dashboard.eitc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_fully_refundable_eitc()
    else:
        return None


ut_fully_refundable_eitc = create_ut_fully_refundable_eitc_reform(
    None, None, bypass=True
)
