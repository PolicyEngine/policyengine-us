from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_aca_ptc_immigration_status() -> Reform:

    def modify_parameters(parameters):
        parameters.gov.aca.ineligible_immigration_statuses.update(
            start=instant("2027-01-01"),
            stop=instant("2035-12-31"),
            value=[
                "ASYLEE",
                "DACA_TPS",  # daca is eligible
                "DEPORTATION_WITHHELD",
                "PAROLED_ONE_YEAR",
                "UNDOCUMENTED",
                "TPS",  # tps is  NOT eligible
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.modify_parameters(modify_parameters)

    return reform


def create_aca_ptc_immigration_status_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_aca_ptc_immigration_status()

    p = parameters.gov.contrib.reconciliation.aca_ptc_immigration_status

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_aca_ptc_immigration_status()
    else:
        return None


aca_ptc_immigration_status = create_aca_ptc_immigration_status_reform(
    None, None, bypass=True
)
