from openfisca_us.model_api import *


class capped_heat_pump_heat_pump_water_heater_biomass_stove_boiler_credit(
    Variable
):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    documentation = "Capped credit on heat pumps, heat pump water heaters, and biomass stoves and boilers"
    unit = USD
    reference = "https://www.democrats.senate.gov/imo/media/doc/inflation_reduction_act_of_2022.pdf#page=340"

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.credits.energy_efficient_home_improvement
        expenditure = add(
            tax_unit,
            period,
            p.qualified_expenditures.heat_pump_heat_pump_water_heater_biomass_stove_boiler,
        )
        rate = p.rates.property
        uncapped = expenditure * rate
        return min_(
            uncapped,
            p.cap.annual.heat_pump_heat_pump_water_heater_biomass_stove_boiler,
        )
