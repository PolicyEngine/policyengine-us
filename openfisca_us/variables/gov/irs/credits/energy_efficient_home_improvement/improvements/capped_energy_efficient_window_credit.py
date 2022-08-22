from openfisca_us.model_api import *


class capped_energy_efficient_window_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = (
        "Capped credit on energy-efficient exterior window and skylights"
    )
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339"

    def formula(tax_unit, period, parameters):
        expenditure = tax_unit("energy_efficient_window_expenditures", period)
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        rate = p.rates.improvements
        uncapped = expenditure * rate
        # First cap by year, then lifetime.
        capped_annual = min_(uncapped, p.cap.annual.window)
        prior_credits = tax_unit(
            "prior_energy_efficient_window_credits", period
        )
        return min_(capped_annual, p.cap.lifetime.window - prior_credits)
