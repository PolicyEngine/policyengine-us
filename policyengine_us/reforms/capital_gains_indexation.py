from policyengine_us.model_api import *
from policyengine_core.periods import instant


def create_capital_gains_indexation_reform(
    purchase_year_threshold: int,
    minimum_holding_period: int = 1,
    cap_adjustment_to_gain: bool = True,
):
    def modify_parameters(parameters):
        indexation = parameters.gov.irs.capital_gains.indexation
        start = instant("2026-01-01")
        stop = instant("2100-12-31")
        indexation.applies.update(start=start, stop=stop, value=True)
        indexation.minimum_holding_period.update(
            start=start, stop=stop, value=minimum_holding_period
        )
        indexation.purchase_year_threshold.update(
            start=start, stop=stop, value=purchase_year_threshold
        )
        indexation.cap_adjustment_to_gain.update(
            start=start, stop=stop, value=cap_adjustment_to_gain
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


capital_gains_indexation_prospective = create_capital_gains_indexation_reform(
    purchase_year_threshold=2025
)
capital_gains_indexation_retrospective = create_capital_gains_indexation_reform(
    purchase_year_threshold=0
)
capital_gains_indexation_retrospective_losses_allowed = (
    create_capital_gains_indexation_reform(
        purchase_year_threshold=0,
        cap_adjustment_to_gain=False,
    )
)
