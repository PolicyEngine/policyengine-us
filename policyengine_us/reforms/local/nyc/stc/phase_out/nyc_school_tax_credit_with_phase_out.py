from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_nyc_school_tax_credit_with_phase_out() -> Reform:
    class nyc_school_tax_credit_phase_out(Variable):
        value_type = float
        unit = USD
        entity = TaxUnit
        label = "NYC School Tax Credit Phase Out"
        definition_period = YEAR
        defined_for = "in_nyc"
        reference = "https://www.nysenate.gov/legislation/bills/2025/S2238"

        def formula(tax_unit, period, parameters):
            agi = tax_unit("ny_agi", period)
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            surviving_spouse = (
                filing_status == filing_status.possible_values.SURVIVING_SPOUSE
            )
            joint_filers = joint | surviving_spouse
            p = parameters(period).gov.contrib.local.nyc.stc.phase_out.rate
            return where(
                joint_filers,
                p.joint_and_surviving_spouse.calc(agi),
                p.other.calc(agi),
            )

    class nyc_school_tax_credit(Variable):
        value_type = float
        entity = TaxUnit
        label = "NYC School Tax Credit"
        unit = USD
        definition_period = YEAR
        defined_for = "in_nyc"
        reference = "https://www.nysenate.gov/legislation/bills/2025/S2238"

        def formula(tax_unit, period, parameters):
            base_amount = add(
                tax_unit,
                period,
                [
                    "nyc_school_tax_credit_fixed_amount",
                    "nyc_school_tax_credit_rate_reduction_amount",
                ],
            )
            phase_out = tax_unit("nyc_school_tax_credit_phase_out", period)
            return max_(0, base_amount - phase_out)

    class reform(Reform):
        def apply(self):
            self.update_variable(nyc_school_tax_credit_phase_out)
            self.update_variable(nyc_school_tax_credit)

    return reform


def create_nyc_school_tax_credit_with_phase_out_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_nyc_school_tax_credit_with_phase_out()

    p = parameters.gov.contrib.local.nyc.stc.phase_out

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_nyc_school_tax_credit_with_phase_out()
    else:
        return None


nyc_school_tax_credit_with_phase_out = (
    create_nyc_school_tax_credit_with_phase_out_reform(None, None, bypass=True)
)
