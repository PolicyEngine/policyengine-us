from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ctc_per_child_phase_in() -> Reform:
    class ctc_phase_in_relevant_earnings(Variable):
        value_type = float
        entity = TaxUnit
        label = "Relevant earnings for the CTC phase-in"
        unit = USD
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/24#d"

        def formula(tax_unit, period, parameters):

            ctc = parameters(period).gov.irs.credits.ctc

            earnings = tax_unit("tax_unit_earned_income", period)
            earnings_over_threshold = max_(
                0, earnings - ctc.refundable.phase_in.threshold
            )
            qualifying_children = tax_unit("ctc_qualifying_children", period)
            phase_in_rate = ctc.refundable.phase_in.rate * qualifying_children
            return earnings_over_threshold * phase_in_rate

    class reform(Reform):
        def apply(self):
            self.update_variable(ctc_phase_in_relevant_earnings)

    return reform


def create_ctc_per_child_phase_in_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ctc_per_child_phase_in()

    p = parameters.gov.contrib.ctc.per_child_phase_in

    reform_active = False
    current_period = period_(period)
    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ctc_per_child_phase_in()
    else:
        return None


ctc_per_child_phase_in = create_ctc_per_child_phase_in_reform(
    None, None, bypass=True
)
