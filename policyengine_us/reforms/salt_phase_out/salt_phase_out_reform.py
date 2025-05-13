from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_salt_phase_out() -> Reform:
    class salt_deduction(Variable):
        value_type = float
        entity = TaxUnit
        label = "SALT deduction"
        unit = USD
        documentation = "State and local taxes plus real estate tax deduction from taxable income."
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/164"

        def formula(tax_unit, period, parameters):
            p = parameters(
                period
            ).gov.irs.deductions.itemized.salt_and_real_estate
            salt_amount = tax_unit("reported_salt", period)
            filing_status = tax_unit("filing_status", period)
            cap = p.cap[filing_status]
            p_ref = parameters(period).gov.contrib.salt_phase_out
            income = tax_unit("adjusted_gross_income", period)
            phase_out = select(
                [
                    filing_status == filing_status.possible_values.SEPARATE,
                    filing_status == filing_status.possible_values.JOINT,
                    filing_status
                    == filing_status.possible_values.HEAD_OF_HOUSEHOLD,
                    filing_status
                    == filing_status.possible_values.SURVIVING_SPOUSE,
                    filing_status == filing_status.possible_values.SINGLE,
                ],
                [
                    p_ref.rate.separate.calc(income),
                    p_ref.rate.joint.calc(income),
                    p_ref.rate.head_of_household.calc(income),
                    p_ref.rate.surviving_spouse.calc(income),
                    p_ref.rate.single.calc(income),
                ],
            )
            capped_salt = min_(cap, salt_amount)
            if p_ref.floor.applies:
                return max_(
                    p_ref.floor.amount[filing_status], capped_salt - phase_out
                )
            return max_(0, capped_salt - phase_out)

    class reform(Reform):
        def apply(self):
            self.update_variable(salt_deduction)

    return reform


def create_salt_phase_out_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_salt_phase_out()

    p = parameters.gov.contrib.salt_phase_out

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_salt_phase_out()
    else:
        return None


salt_phase_out_reform = create_salt_phase_out_reform(None, None, bypass=True)
