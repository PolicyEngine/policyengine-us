from openfisca_us.model_api import *


class capped_energy_efficient_window_expenditures(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "Capped expenditures on energy-efficient exterior window and skylights"
    )
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339"

    def formula(tax_unit, period, parameters):
        uncapped = tax_unit("energy_efficient_window_expenditures", period)
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        return min_(uncapped, p.cap.annual.window)
