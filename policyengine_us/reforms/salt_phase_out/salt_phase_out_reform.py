from policyengine_us.model_api import *
from policyengine_core.periods import period as period_


def create_salt_phase_out() -> Reform:

    class salt_cap(Variable):
        value_type = float
        entity = TaxUnit
        label = "SALT cap"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/164"

        def formula(tax_unit, period, parameters):
            filing_status = tax_unit("filing_status", period)
            p = parameters(
                period
            ).gov.irs.deductions.itemized.salt_and_real_estate
            max_cap = p.cap[filing_status]
            p_ref = parameters(period).gov.contrib.salt_phase_out
            agi = tax_unit("adjusted_gross_income", period)
            agi_excess = max_(0, agi - p_ref.threshold[filing_status])
            phase_out = p_ref.rate * agi_excess
            phased_out_cap = max_(0, max_cap - phase_out)
            if p_ref.floor.applies:
                floor = p_ref.floor.amount[filing_status]
                return max_(phased_out_cap, floor)
            return phased_out_cap

    class reform(Reform):
        def apply(self):
            self.update_variable(salt_cap)

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
