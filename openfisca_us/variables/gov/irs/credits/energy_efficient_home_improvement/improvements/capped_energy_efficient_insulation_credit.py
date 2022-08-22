from openfisca_us.model_api import *


class capped_energy_efficient_insulation_credit(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped credit on energy-efficient insulation material"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=339"

    def formula(tax_unit, period, parameters):
        expenditure = tax_unit(
            "energy_efficient_insulation_expenditures", period
        )
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        rate = p.rates.improvements
        uncapped = expenditure * rate
        return min_(uncapped, p.cap.annual.insulation_material)
