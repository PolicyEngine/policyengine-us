from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_ut_hb210() -> Reform:
    """
    Utah HB 210 (2026) - Tax penalty removal bill that:
    1. Adds a taxpayer credit add-on for married filers ($543 MFS, $1,086 joint)
    2. Removes marriage penalties from phaseout thresholds (parameter changes)
    3. Repeals the Utah EITC (parameter change - set rate to 0)

    This reform implements provision #1 (the structural change).
    Provisions #2 and #3 can be modeled via parameter changes.
    """

    class ut_taxpayer_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "Utah taxpayer credit"
        unit = USD
        documentation = "Form TC-40, line 20"
        definition_period = YEAR
        defined_for = StateCode.UT
        reference = (
            "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1018.html",
            "https://le.utah.gov/~2026/bills/static/HB0210.html",
        )

        def formula(tax_unit, period, parameters):
            # Base maximum credit (6% of deductions + exemption)
            base_max = tax_unit("ut_taxpayer_credit_max", period)

            # Add the married filer add-on per HB 210 Section 59-10-1018(3)
            # The add-on is added before phaseout is applied
            filing_status = tax_unit("filing_status", period)
            p = parameters(
                period
            ).gov.contrib.states.ut.hb210.taxpayer_credit_add_on
            add_on = p.amount[filing_status]

            # Total maximum credit including add-on
            total_max = base_max + add_on

            # Apply phaseout reduction to total credit (including add-on)
            reduction = tax_unit("ut_taxpayer_credit_reduction", period)
            return max_(total_max - reduction, 0)

    class reform(Reform):
        def apply(self):
            self.update_variable(ut_taxpayer_credit)

    return reform


def create_ut_hb210_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_ut_hb210()

    p = parameters.gov.contrib.states.ut.hb210

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ut_hb210()
    else:
        return None


ut_hb210 = create_ut_hb210_reform(None, None, bypass=True)
