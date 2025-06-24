from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_reconciliation_cdcc() -> Reform:
    class cdcc_rate(Variable):
        value_type = float
        entity = TaxUnit
        label = "CDCC credit rate"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/21#a_2"

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.irs.credits.cdcc
            agi = tax_unit("adjusted_gross_income", period)

            # First phase-out
            excess_agi = max_(0, agi - p.phase_out.start)
            increments = np.ceil(excess_agi / p.phase_out.increment)
            percentage_reduction = increments * p.phase_out.rate
            phased_out_rate = max_(
                p.phase_out.min, p.phase_out.max - percentage_reduction
            )

            # Second phase-out
            p_ref = parameters(period).gov.contrib.reconciliation.cdcc
            filing_status = tax_unit("filing_status", period)
            second_phase_out_start = p_ref.phase_out.second_start[
                filing_status
            ]
            second_excess_agi = max_(0, agi - second_phase_out_start)
            second_phase_out_increment = p_ref.phase_out.second_increment[
                filing_status
            ]
            second_increments = np.ceil(
                second_excess_agi / second_phase_out_increment
            )
            second_percentage_reduction = second_increments * p.phase_out.rate
            return max_(
                p_ref.phase_out.second_min,
                phased_out_rate - second_percentage_reduction,
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(cdcc_rate)

    return reform


def create_reconciliation_cdcc_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_reconciliation_cdcc()

    p = parameters.gov.contrib.reconciliation.cdcc

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_reconciliation_cdcc()
    else:
        return None


reconciliation_cdcc = create_reconciliation_cdcc_reform(
    None, None, bypass=True
)
